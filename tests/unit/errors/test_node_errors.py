"""NodeError behaviour of the Decart nodes, through the real `requests` path.

A local HTTP server stands in for api.decart.ai, so the errors come from `requests` itself.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest
from griptape_nodes.exe_types.core_types import NodeError
from griptape_nodes.retained_mode.griptape_nodes import GriptapeNodes

LIBRARY_DIR = Path(__file__).resolve().parents[3] / "decart"
MANIFEST = json.loads((LIBRARY_DIR / "griptape_nodes_library.json").read_text())
NODES = [(n["class_name"], n["file_path"]) for n in MANIFEST["nodes"]]

RETIRED = {"detail": "This model has been retired. See https://docs.example/models.", "model": "lucy-pro-t2i"}
VALIDATION = {"detail": [{"type": "missing", "loc": ["body", "data"], "msg": "Field required", "input": None}]}


def load_node_class(class_name: str, file_name: str):
    """Load a node file the way the engine does: standalone, library folder on sys.path, no package."""
    sys.path.insert(0, str(LIBRARY_DIR))
    sys.modules["decart"] = None  # type: ignore[assignment]
    try:
        spec = importlib.util.spec_from_file_location(f"_engine_style_{file_name[:-3]}", LIBRARY_DIR / file_name)
        assert spec is not None
        assert spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(LIBRARY_DIR))
        del sys.modules["decart"]
    return getattr(module, class_name)


class FakeDecart:
    """Serves one canned response for every POST."""

    def __init__(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):  # noqa: N802
                self.rfile.read(int(self.headers.get("content-length", 0)))
                self.send_response(outer.status)
                self.send_header("content-type", outer.content_type)
                self.send_header("x-request-id", "req-123")
                self.send_header("content-length", str(len(outer.body)))
                self.end_headers()
                self.wfile.write(outer.body)

            def log_message(self, *args):
                pass

        self.status, self.body, self.content_type = status, body, content_type
        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    @property
    def url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}/v1/generate/"

    def close(self) -> None:
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def fake():
    servers = []

    def make(status, body, content_type="application/json"):
        server = FakeDecart(status, body if isinstance(body, bytes) else json.dumps(body).encode(), content_type)
        servers.append(server)
        return server

    yield make
    for server in servers:
        server.close()


@pytest.fixture
def with_key(monkeypatch):
    monkeypatch.setattr(GriptapeNodes.SecretsManager(), "get_secret", lambda *_a, **_k: "test-key", raising=False)


def make_node(class_name: str, file_name: str, **values):
    node = load_node_class(class_name, file_name)(name="decart-node")
    defaults: dict[str, object] = {"prompt": "a cat"}
    if "i2" in file_name or "v2v" in file_name or "edit" in file_name:
        key = "image_input" if "i2" in file_name else "video_input"
        defaults[key] = {"type": "image/png", "value": "data:image/png;base64,eA=="}
    for name, value in {**defaults, **values}.items():
        node.parameter_values[name] = value
    return node


T2I = ("DecartLucyProT2I", "decart_lucy_pro_t2i.py")


@pytest.mark.parametrize(("class_name", "file_name"), NODES)
def test_node_loads_engine_style(class_name, file_name):
    assert load_node_class(class_name, file_name).__name__ == class_name


@pytest.mark.parametrize(("class_name", "file_name"), NODES)
def test_missing_key_is_the_only_validation_error(class_name, file_name, monkeypatch):
    monkeypatch.setattr(GriptapeNodes.SecretsManager(), "get_secret", lambda *_a, **_k: None, raising=False)
    node = make_node(class_name, file_name, prompt="")
    errors = node.validate_before_node_run()
    assert errors is not None
    assert len(errors) == 1
    error = errors[0]
    assert isinstance(error, NodeError)
    assert "DECART_API_KEY is not set" in str(error)
    assert error.links[0].url == "#settings-secrets?filter=DECART_API_KEY"
    assert node.name not in str(error)


@pytest.mark.parametrize(("class_name", "file_name"), NODES)
def test_process_without_key_raises(class_name, file_name, monkeypatch):
    monkeypatch.setattr(GriptapeNodes.SecretsManager(), "get_secret", lambda *_a, **_k: None, raising=False)
    with pytest.raises(NodeError, match="DECART_API_KEY is not set"):
        make_node(class_name, file_name)._process()


@pytest.mark.parametrize(("class_name", "file_name"), NODES)
def test_key_present_passes_validation(class_name, file_name, with_key):
    assert make_node(class_name, file_name).validate_before_node_run() is None


def test_missing_prompt(with_key):
    with pytest.raises(NodeError) as info:
        make_node(*T2I, prompt="")._process()
    assert str(info.value) == "Enter a prompt in 'Prompt'."
    assert info.value.fields == {"parameter": "prompt"}


def test_missing_image(with_key):
    with pytest.raises(NodeError) as info:
        make_node("DecartLucyProI2I", "decart_lucy_pro_i2i.py", image_input=None)._process()
    assert str(info.value) == "Connect an image to 'Input Image'."
    assert info.value.fields == {"parameter": "image_input"}


def test_missing_video(with_key):
    with pytest.raises(NodeError) as info:
        make_node("DecartLucyDevV2V", "decart_lucy_dev_v2v.py", video_input=None)._process()
    assert str(info.value) == "Connect a video to 'Input Video'."


def test_unreadable_image_value(with_key):
    with pytest.raises(NodeError) as info:
        make_node(
            "DecartLucyProI2I", "decart_lucy_pro_i2i.py", image_input={"value": "nope", "type": "image/png"}
        )._process()
    assert "'Input Image'" in str(info.value)
    assert info.value.fields == {"parameter": "image_input"}


def run_against(node, server):
    node.BASE_URL = server.url
    return node._process()


def test_retired_model_has_message_status_response_and_link(with_key, fake):
    server = fake(410, RETIRED)
    with pytest.raises(NodeError) as info:
        run_against(make_node(*T2I), server)
    error = info.value
    assert str(error) == RETIRED["detail"]
    assert error.fields == {"status_code": 410, "request_id": "req-123"}
    assert error.response == RETIRED
    assert [link.label for link in error.links] == ["Available Decart models"]


def test_refused_key_links_to_settings(with_key, fake):
    server = fake(401, {"detail": "Invalid API key"})
    with pytest.raises(NodeError) as info:
        run_against(make_node(*T2I), server)
    error = info.value
    assert str(error) == "Decart refused the API key: Invalid API key. Update it in Settings and run the node again."
    assert error.links[0].url == "#settings-secrets?filter=DECART_API_KEY"
    assert error.fields["status_code"] == 401


def test_validation_list_is_read(with_key, fake):
    server = fake(422, VALIDATION)
    with pytest.raises(NodeError) as info:
        run_against(make_node(*T2I), server)
    assert str(info.value) == "data: Field required"
    assert info.value.response == VALIDATION


def test_non_json_body_is_attached_as_text(with_key, fake):
    server = fake(502, b"<html>Bad gateway</html>", "text/html")
    with pytest.raises(NodeError) as info:
        run_against(make_node(*T2I), server)
    assert str(info.value) == "Decart returned an error (HTTP 502)."
    assert info.value.response == {"text": "<html>Bad gateway</html>"}


def test_connection_failure(with_key, fake):
    server = fake(200, b"")
    url = server.url
    server.close()
    node = make_node(*T2I)
    node.BASE_URL = url
    with pytest.raises(NodeError, match="Could not connect to Decart"):
        node._process()


def test_empty_success_body(with_key, fake):
    server = fake(200, b"", "image/png")
    with pytest.raises(NodeError, match="empty response with no image data"):
        run_against(make_node(*T2I), server)
