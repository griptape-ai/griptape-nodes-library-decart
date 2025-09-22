from __future__ import annotations

import base64
import logging
import uuid
from io import BytesIO

import requests

from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import AsyncResult, DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.traits.options import Options
from griptape_nodes_library.video.video_url_artifact import VideoUrlArtifact

logger = logging.getLogger(__name__)

__all__ = ["DecartLucyVideoEdit"]

class DecartLucyVideoEdit(DataNode):

    """Generate a video using the Decart Lucy Video Edit API.

    Args:
        video_input: The input video to process.
        prompt: The prompt to process.
        video_output: The output video from Decart Lucy Video Edit.

    """


    SERVICE_NAME = "Decart"
    API_KEY_ENV_VAR = "DECART_API_KEY"
    BASE_URL = "https://api.decart.ai/v1/generate/"
    MODEL_NAME = "lucy-pro-v2v"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.add_parameter(
            Parameter(
                name="video_input",
                tooltip="Input video to edit",
                type="VideoUrlArtifact",
                input_types=["VideoUrlArtifact", "VideoArtifact"],
                allowed_modes={ParameterMode.INPUT,ParameterMode.PROPERTY,ParameterMode.OUTPUT},
                ui_options={"display_name": "Input Video"}
            )
        )
        self.add_parameter(
            Parameter(
                name="prompt",
                tooltip="Prompt to edit the video",
                type="str",
                allowed_modes={ParameterMode.INPUT,ParameterMode.PROPERTY,ParameterMode.OUTPUT},
                ui_options={"display_name": "Prompt",
                            "placeholder_text": "Describe the video edit you want to make...",
                            "multiline": True},
            )
        )
        self.add_parameter(
            Parameter(
                name="video_output",
                tooltip="Output video from Decart Lucy Video Edit",
                type="VideoUrlArtifact",
                output_type="VideoUrlArtifact",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"display_name": "Output Video"}
            )
        )

    def validate_node(self) -> list[Exception] | None:
        return None

    def _convert_video_to_file_payload(self, video_input) -> dict:
        """Convert VideoUrlArtifact, VideoArtifact, or dict to the correct file payload for API submission.
        
        This method converts the video artifact into the format expected by the Decart API,
        which expects a file-like object under the "data" key in the files parameter.
        
        Args:
            video_input: VideoUrlArtifact, VideoArtifact instance, or dict representation
            
        Returns:
            dict: Files payload in the format {"data": (filename, file_bytes, content_type)}
        """
        if isinstance(video_input, dict):
            # Handle dictionary input
            value = video_input.get("value", "")
            video_type = video_input.get("type", "video/mp4")
            
            if "base64," in value:
                # Handle base64-encoded video data
                base64_data = value.split("base64,")[1] if "base64," in value else value
                video_bytes = base64.b64decode(base64_data)
                filename = "input.mp4"
                
                # Extract format from type if available
                if "/" in video_type:
                    extension = video_type.split("/")[1]
                    filename = f"input.{extension}"
                    
            elif value.startswith(("http://", "https://")):
                # Handle URL in dictionary
                response = requests.get(value)
                response.raise_for_status()
                video_bytes = response.content
                
                # Extract filename from URL
                url_path = value.split('/')[-1]
                filename = url_path if '.' in url_path and len(url_path.split('.')[-1]) <= 4 else "input.mp4"
                
            else:
                raise ValueError(f"Unsupported video dictionary value format: {value[:50]}...")
                
        elif hasattr(video_input, 'to_bytes'):
            # For UrlArtifact-based artifacts (VideoUrlArtifact)
            video_bytes = video_input.to_bytes()
            # Extract filename from URL if possible, otherwise use default
            filename = "input.mp4"
            if hasattr(video_input, 'value') and isinstance(video_input.value, str):
                url_path = video_input.value.split('/')[-1]
                if '.' in url_path and len(url_path.split('.')[-1]) <= 4:
                    filename = url_path
                    
        elif hasattr(video_input, 'value') and isinstance(video_input.value, bytes):
            # For direct bytes artifacts
            video_bytes = video_input.value
            filename = "input.mp4"
            
        else:
            raise ValueError(f"Unsupported video input type: {type(video_input)}")
        
        # Create BytesIO object for the file-like interface
        video_file = BytesIO(video_bytes)
        
        # Return the files payload in the format expected by requests
        # This mimics: files = {"data": open("/path/to/input.mp4", "rb")}
        return {"data": (filename, video_file, "video/mp4")}

    def _convert_response_to_video_url_artifact(self, response_content: bytes) -> VideoUrlArtifact:
        """Convert API response content (video bytes) to a VideoUrlArtifact.
        
        This method takes the raw video bytes from the API response and creates
        a VideoUrlArtifact by saving the video to the static file server.
        
        Args:
            response_content: Raw video bytes from the API response
            
        Returns:
            VideoUrlArtifact: Artifact containing the URL to the saved video
        """
        if not response_content:
            raise ValueError("Empty response content - no video data received")
        
        # Generate a unique filename for the output video
        filename = f"decart_output_{uuid.uuid4()}.mp4"
        
        # Save the video bytes to the static file server
        url = GriptapeNodes.StaticFilesManager().save_static_file(response_content, filename)
        
        # Create and return VideoUrlArtifact with the URL
        return VideoUrlArtifact(url)

    def process(self) -> AsyncResult[None]:
        yield lambda: self._process()

    def _process(self):
        api_key = self._validate_api_key()
        headers = {"X-API-KEY": f"{api_key}"}
        video_input = self.get_parameter_value("video_input")
        prompt = self.get_parameter_value("prompt")

        if not video_input:
            raise ValueError("No input video provided")

        if not prompt:
            raise ValueError("No prompt provided")

        # Convert video input to the correct file payload format
        files_payload = self._convert_video_to_file_payload(video_input)

        # Make API request
        api_url = f"{self.BASE_URL}{self.MODEL_NAME}"
        logger.info(f"Sending video edit request to Decart API: {api_url}")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data={"prompt": prompt},
                files=files_payload
            )
            
            logger.info(f"API response received: status_code={response.status_code}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            response_size = len(response.content)
            logger.info(f"Successfully received edited video: {response_size} bytes")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Decart API request failed: {e}")
            raise

        # Convert response content to VideoUrlArtifact
        output_video = self._convert_response_to_video_url_artifact(response.content)
        
        # Publish the VideoUrlArtifact to the output parameter
        self.publish_update_to_parameter("video_output", output_video)

        return output_video 
        
    def _validate_api_key(self) -> str:
        api_key = self.get_config_value(service=self.SERVICE_NAME, value=self.API_KEY_ENV_VAR)
        if not api_key:
            msg = f"{self.name} is missing {self.API_KEY_ENV_VAR}. Ensure it's set in the environment/config."
            raise ValueError(msg)
        return api_key

