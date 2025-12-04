from __future__ import annotations

import base64
import logging
import uuid
from io import BytesIO

import requests

from griptape.artifacts import ImageArtifact, ImageUrlArtifact, VideoUrlArtifact
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import AsyncResult, DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.events.os_events import ExistingFilePolicy

logger = logging.getLogger(__name__)

class DecartLucyDevI2V(DataNode):

    """Generate a video from an image using the Decart Lucy Dev I2V API.

    Args:
        image_input: The input image to convert to video.
        prompt: The prompt to guide video generation.
        seed: Optional seed for reproducible generation.
        video_output: The output video from Decart Lucy Dev I2V.

    Note:
        Dev model only supports 720p resolution (read-only parameter).

    """

    SERVICE_NAME = "Decart"
    API_KEY_ENV_VAR = "DECART_API_KEY"
    BASE_URL = "https://api.decart.ai/v1/generate/"
    MODEL_NAME = "lucy-dev-i2v"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

        self.add_parameter(
            Parameter(
                name="image_input",
                tooltip="Input image to convert to video",
                type="ImageUrlArtifact",
                input_types=["ImageUrlArtifact", "ImageArtifact"],
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                ui_options={"display_name": "Input Image"}
            )
        )
        self.add_parameter(
            Parameter(
                name="prompt",
                tooltip="Text prompt for video generation",
                type="str",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                ui_options={"display_name": "Prompt",
                            "placeholder_text": "Describe the video you want to generate...",
                            "multiline": True},
            )
        )
        self.add_parameter(
            Parameter(
                name="seed",
                tooltip="Seed for reproducible generation",
                type="int",
                default_value=None,
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                ui_options={"display_name": "Seed"}
            )
        )
        self.add_parameter(
            Parameter(
                name="resolution",
                tooltip="Video resolution (read-only, Dev model only supports 720p)",
                type="str",
                default_value="720p",
                allowed_modes={ParameterMode.PROPERTY},
                settable=False,
                ui_options={"display_name": "Resolution"}
            )
        )
        self.add_parameter(
            Parameter(
                name="video_output",
                tooltip="Output video from Decart Lucy Dev I2V",
                type="VideoUrlArtifact",
                output_type="VideoUrlArtifact",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"display_name": "Output Video"}
            )
        )

    def validate_node(self) -> list[Exception] | None:
        return None

    def _convert_image_to_file_payload(self, image_input) -> dict:
        """Convert ImageUrlArtifact, ImageArtifact, or dict to the correct file payload for API submission.
        
        This method converts the image artifact into the format expected by the Decart API,
        which expects a file-like object under the "data" key in the files parameter.
        
        Args:
            image_input: ImageUrlArtifact, ImageArtifact instance, or dict representation
            
        Returns:
            dict: Files payload in the format {"data": (filename, file_bytes, content_type)}
        """
        if isinstance(image_input, dict):
            # Handle dictionary input
            value = image_input.get("value", "")
            image_type = image_input.get("type", "image/png")
            
            if "base64," in value:
                # Handle base64-encoded image data
                base64_data = value.split("base64,")[1] if "base64," in value else value
                image_bytes = base64.b64decode(base64_data)
                filename = "input.png"
                
                # Extract format from type if available
                if "/" in image_type:
                    extension = image_type.split("/")[1]
                    filename = f"input.{extension}"
                    
            elif value.startswith(("http://", "https://")):
                # Handle URL in dictionary
                response = requests.get(value)
                response.raise_for_status()
                image_bytes = response.content
                
                # Extract filename from URL
                url_path = value.split('/')[-1]
                filename = url_path if '.' in url_path and len(url_path.split('.')[-1]) <= 4 else "input.png"
                
            else:
                raise ValueError(f"Unsupported image dictionary value format: {value[:50]}...")
                
        elif hasattr(image_input, 'to_bytes'):
            # For UrlArtifact-based artifacts (ImageUrlArtifact)
            image_bytes = image_input.to_bytes()
            # Extract filename from URL if possible, otherwise use default
            filename = "input.png"
            if hasattr(image_input, 'value') and isinstance(image_input.value, str):
                url_path = image_input.value.split('/')[-1]
                if '.' in url_path and len(url_path.split('.')[-1]) <= 4:
                    filename = url_path
                    
        elif hasattr(image_input, 'value') and isinstance(image_input.value, bytes):
            # For direct bytes artifacts
            image_bytes = image_input.value
            filename = "input.png"
            
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")
        
        # Create BytesIO object for the file-like interface
        image_file = BytesIO(image_bytes)
        
        # Return the files payload in the format expected by requests
        # This mimics: files = {"data": open("/path/to/input.png", "rb")}
        return {"data": (filename, image_file, "image/png")}

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
        filename = f"decart_i2v_output_{uuid.uuid4()}.mp4"
        
        # Save the video bytes to the static file server
        url = GriptapeNodes.StaticFilesManager().save_static_file(response_content, filename, ExistingFilePolicy.CREATE_NEW)
        
        # Create and return VideoUrlArtifact with the URL
        return VideoUrlArtifact(url)

    def process(self) -> AsyncResult[None]:
        yield lambda: self._process()

    def _process(self):
        api_key = self._validate_api_key()
        headers = {"X-API-KEY": f"{api_key}"}
        image_input = self.get_parameter_value("image_input")
        prompt = self.get_parameter_value("prompt")
        seed = self.get_parameter_value("seed")
        resolution = self.get_parameter_value("resolution")

        if not image_input:
            raise ValueError("No input image provided")

        if not prompt:
            raise ValueError("No prompt provided")

        # Convert image input to the correct file payload format
        files_payload = self._convert_image_to_file_payload(image_input)

        # Prepare data payload
        data_payload = {"prompt": prompt}
        if seed is not None:
            data_payload["seed"] = seed
        if resolution:
            data_payload["resolution"] = resolution

        # Debug logging for request payload
        logger.debug(f"API request payload: {data_payload}")
        logger.debug(f"Files payload keys: {list(files_payload.keys())}")
        if files_payload:
            for key, (filename, file_obj, content_type) in files_payload.items():
                file_size = len(file_obj.getvalue()) if hasattr(file_obj, 'getvalue') else 'unknown'
                logger.debug(f"File {key}: filename={filename}, content_type={content_type}, size={file_size} bytes")

        # Make API request
        api_url = f"{self.BASE_URL}{self.MODEL_NAME}"
        logger.info(f"Sending image-to-video request to Decart API: {api_url}")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=data_payload,
                files=files_payload
            )
            
            logger.info(f"API response received: status_code={response.status_code}")
            logger.debug(f"Response headers: {dict(response.headers)}")
            
            # Check if the request was successful
            response.raise_for_status()
            
            response_size = len(response.content)
            logger.info(f"Successfully received generated video: {response_size} bytes")
            logger.debug(f"Response content type: {response.headers.get('content-type', 'unknown')}")
            
            # Log truncated response for binary content
            if response_size > 0:
                content_preview = response.content[:100] if response_size > 100 else response.content
                logger.debug(f"Response content preview (first 100 bytes): {content_preview}")
            else:
                logger.debug("Response content is empty")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Decart API request failed: {e}")
            raise

        # Convert response content to VideoUrlArtifact
        output_video = self._convert_response_to_video_url_artifact(response.content)
        
        # Publish the VideoUrlArtifact to the output parameter
        self.publish_update_to_parameter("video_output", output_video)

        return output_video 
        
    def _validate_api_key(self) -> str:
        api_key = GriptapeNodes.SecretsManager().get_secret(self.API_KEY_ENV_VAR)
        if not api_key:
            msg = f"{self.name} is missing {self.API_KEY_ENV_VAR}. Ensure it's set in the environment/config."
            raise ValueError(msg)
        return api_key
