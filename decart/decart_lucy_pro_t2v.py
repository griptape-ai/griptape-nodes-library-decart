from __future__ import annotations

import logging
import uuid

import requests

from griptape.artifacts import VideoUrlArtifact
from griptape_nodes.exe_types.core_types import Parameter, ParameterMode
from griptape_nodes.exe_types.node_types import AsyncResult, DataNode
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes
from griptape_nodes.retained_mode.events.os_events import ExistingFilePolicy
from griptape_nodes.traits.options import Options

logger = logging.getLogger(__name__)

class DecartLucyProT2V(DataNode):

    """Generate a video from text using the Decart Lucy Pro T2V API.

    Args:
        prompt: The text prompt to generate video from.
        seed: Optional seed for reproducible generation.
        resolution: Video resolution - 720p (default) or 480p.
        orientation: Video orientation - landscape (default) or portrait.
        video_output: The output video from Decart Lucy Pro T2V.

    """

    SERVICE_NAME = "Decart"
    API_KEY_ENV_VAR = "DECART_API_KEY"
    BASE_URL = "https://api.decart.ai/v1/generate/"
    MODEL_NAME = "lucy-pro-t2v"

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

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
                tooltip="Video resolution",
                type="str",
                default_value="720p",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                ui_options={"display_name": "Resolution"},
                traits={Options(choices=["720p", "480p"])}
            )
        )
        self.add_parameter(
            Parameter(
                name="orientation",
                tooltip="Video orientation",
                type="str",
                default_value="landscape",
                allowed_modes={ParameterMode.INPUT, ParameterMode.PROPERTY, ParameterMode.OUTPUT},
                ui_options={"display_name": "Orientation"},
                traits={Options(choices=["landscape", "portrait"])}
            )
        )
        self.add_parameter(
            Parameter(
                name="video_output",
                tooltip="Output video from Decart Lucy Pro T2V",
                type="VideoUrlArtifact",
                output_type="VideoUrlArtifact",
                allowed_modes={ParameterMode.OUTPUT},
                ui_options={"display_name": "Output Video"}
            )
        )

    def validate_node(self) -> list[Exception] | None:
        return None

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
        filename = f"decart_t2v_output_{uuid.uuid4()}.mp4"
        
        # Save the video bytes to the static file server
        url = GriptapeNodes.StaticFilesManager().save_static_file(response_content, filename, ExistingFilePolicy.CREATE_NEW)
        
        # Create and return VideoUrlArtifact with the URL
        return VideoUrlArtifact(url)

    def process(self) -> AsyncResult[None]:
        yield lambda: self._process()

    def _process(self):
        api_key = self._validate_api_key()
        headers = {"X-API-KEY": f"{api_key}"}
        prompt = self.get_parameter_value("prompt")
        seed = self.get_parameter_value("seed")
        resolution = self.get_parameter_value("resolution")
        orientation = self.get_parameter_value("orientation")

        if not prompt:
            raise ValueError("No prompt provided")

        # Prepare data payload (no file upload for text-to-video)
        data_payload = {"prompt": prompt}
        if seed is not None:
            data_payload["seed"] = seed
        if resolution:
            data_payload["resolution"] = resolution
        if orientation:
            data_payload["orientation"] = orientation

        # Debug logging for request payload
        logger.debug(f"API request payload: {data_payload}")

        # Make API request
        api_url = f"{self.BASE_URL}{self.MODEL_NAME}"
        logger.info(f"Sending text-to-video request to Decart API: {api_url}")
        
        try:
            response = requests.post(
                api_url,
                headers=headers,
                data=data_payload
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
