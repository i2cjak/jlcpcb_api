from __future__ import annotations

import json
from pathlib import Path

import requests

from jlcpcb_api import (
    JLCAuth,
    JLCPCBClient,
    GetSteelPriceConfigRequest,
    UploadGerberFileRequest,
)


def _json_response(payload: dict) -> requests.Response:
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps(payload).encode("utf-8")
    response.headers["Content-Type"] = "application/json"
    response.headers["J-Trace-ID"] = "trace-123"
    return response


def test_upload_uses_meta_and_file_parts(tmp_path: Path, monkeypatch) -> None:
    board = tmp_path / "board.zip"
    board.write_bytes(b"zip-data")

    client = JLCPCBClient(
        JLCAuth(app_id="app", access_key="ak", secret_key="sk"),
    )

    captured: dict[str, object] = {}

    def fake_send(prepared: requests.PreparedRequest, **_: object) -> requests.Response:
        captured["method"] = prepared.method
        captured["url"] = prepared.url
        body = prepared.body
        if isinstance(body, bytes):
            captured["body"] = body.decode("utf-8", errors="replace")
        else:
            captured["body"] = str(body)
        captured["authorization"] = prepared.headers["Authorization"]
        return _json_response({"code": 200, "message": "ok", "data": "file-key"})

    monkeypatch.setattr(client._session, "send", fake_send)

    result = client.pcb.upload_gerber_file(UploadGerberFileRequest(file=board))

    assert result.is_successful
    assert result.data == "file-key"
    assert captured["method"] == "POST"
    assert str(captured["url"]).endswith("/overseas/openapi/pcb/uploadGerber")
    assert 'name="meta"' in str(captured["body"])
    assert "{}" in str(captured["body"])
    assert 'name="file"; filename="board.zip"' in str(captured["body"])
    assert str(captured["authorization"]).startswith('JOP appid="app",accesskey="ak"')


def test_get_sets_json_content_type(monkeypatch) -> None:
    client = JLCPCBClient(
        JLCAuth(app_id="app", access_key="ak", secret_key="sk"),
    )

    captured: dict[str, object] = {}

    def fake_send(prepared: requests.PreparedRequest, **_: object) -> requests.Response:
        captured["content_type"] = prepared.headers.get("Content-Type")
        captured["accept"] = prepared.headers.get("Accept")
        captured["authorization"] = prepared.headers["Authorization"]
        return _json_response({"code": 200, "message": "ok", "data": []})

    monkeypatch.setattr(client._session, "send", fake_send)

    result = client.pcb.get_steel_price_config(GetSteelPriceConfigRequest())

    assert result.is_successful
    assert captured["content_type"] == "application/json"
    assert captured["accept"] == "application/json"
    assert str(captured["authorization"]).startswith('JOP appid="app",accesskey="ak"')
