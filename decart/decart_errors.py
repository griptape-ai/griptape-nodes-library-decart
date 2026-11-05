"""Turns Decart API failures into NodeError.

Node files import this module by bare name (`from decart_errors import ...`). The engine loads each
node file on its own with the manifest's folder on `sys.path`, so neither the package name nor a
relative import resolves.
"""

from __future__ import annotations

from typing import Any

import requests
from griptape_nodes.exe_types.core_types import NodeError, NodeErrorLink

API_KEY_NAME = "DECART_API_KEY"
API_KEY_URL = "https://platform.decart.ai/"
MODELS_URL = "https://docs.platform.decart.ai/getting-started/models"

_KEY_REFUSED_STATUSES = (401, 403)
_MODEL_RETIRED_STATUS = 410
_RATE_LIMITED_STATUS = 429
_MAX_TEXT_CHARS = 2000


def missing_key_error() -> NodeError:
    """The error for a missing DECART_API_KEY, linking to Settings and to Decart's key page."""
    return NodeError(
        f"{API_KEY_NAME} is not set. Add it in Settings → API Keys & Secrets, then run the node again.",
        links=[
            NodeErrorLink(label="Add the API key", url=f"#settings-secrets?filter={API_KEY_NAME}"),
            NodeErrorLink(label="Get a Decart API key", url=API_KEY_URL),
        ],
    )


def input_error(message: str, parameter: str) -> NodeError:
    """The error for a bad or missing input, naming the parameter in `fields`."""
    return NodeError(message, fields={"parameter": parameter})


def error_from_response(response: requests.Response) -> NodeError:
    """Build a NodeError from a Decart HTTP error response."""
    status = response.status_code
    body = _json_body(response)
    reason = _reason(body)

    fields: dict[str, str | int | float | bool] = {"status_code": status}
    request_id = response.headers.get("x-request-id")
    if request_id:
        fields["request_id"] = request_id

    links: list[NodeErrorLink] = []
    if status in _KEY_REFUSED_STATUSES:
        message = f"Decart refused the API key: {reason.rstrip('.')}." if reason else "Decart refused the API key."
        message += " Update it in Settings and run the node again."
        links.append(NodeErrorLink(label="Update the API key", url=f"#settings-secrets?filter={API_KEY_NAME}"))
        links.append(NodeErrorLink(label="Get a Decart API key", url=API_KEY_URL))
    elif status == _MODEL_RETIRED_STATUS:
        message = reason or "Decart has retired this model."
        links.append(NodeErrorLink(label="Available Decart models", url=MODELS_URL))
    elif status == _RATE_LIMITED_STATUS:
        message = reason or "Decart is rate-limiting requests. Wait a minute and run the node again."
    else:
        message = reason or f"Decart returned an error (HTTP {status})."

    attached = body
    if attached is None and response.text:
        attached = {"text": response.text[:_MAX_TEXT_CHARS]}
    return NodeError(message, fields=fields, response=attached, links=links or None)


def error_from_request_exception(error: requests.exceptions.RequestException) -> NodeError:
    """Build a NodeError from a failed `requests` call, with or without a response."""
    response = error.response
    if response is not None:
        return error_from_response(response)
    if isinstance(error, requests.exceptions.Timeout):
        return NodeError("The request to Decart timed out. Run the node again.")
    if isinstance(error, requests.exceptions.ConnectionError):
        return NodeError("Could not connect to Decart. Check your network connection and run the node again.")
    return NodeError(f"The request to Decart failed: {error}")


def _json_body(response: requests.Response) -> dict[str, Any] | None:
    try:
        body = response.json()
    except ValueError:
        return None
    return body if isinstance(body, dict) and body else None


def _reason(body: dict[str, Any] | None) -> str | None:
    """Decart's own explanation: `detail`, `error` or `message` as text, or the messages in a validation list."""
    if body is None:
        return None
    for key in ("detail", "error", "message"):
        text = _text(body.get(key))
        if text:
            return text
    return None


def _text(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        return _text(value.get("message") or value.get("msg"))
    if isinstance(value, list):
        parts = []
        for item in value:
            if not isinstance(item, dict):
                continue
            msg = _text(item.get("msg") or item.get("message"))
            if not msg:
                continue
            loc = item.get("loc")
            where = ".".join(str(p) for p in loc if p != "body") if isinstance(loc, list) else ""
            parts.append(f"{where}: {msg}" if where else msg)
        return "; ".join(parts) or None
    return None
