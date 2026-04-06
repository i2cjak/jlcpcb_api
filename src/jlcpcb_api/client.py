from __future__ import annotations

import json
import mimetypes
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

import requests

from .auth import JLCAuth
from .errors import JLCBusinessError, JLCProtocolError, JLCTransportError
from .models import (
    ApiRequest,
    ComponentCodesQueryVO,
    ComponentListRequest,
    CustomerPrivateStockListRequest,
    FileAnalysisResultRequest,
    GetComponentInfoRequest,
    GetImpedanceTemplateSettingListRequest,
    GetOnlineCalculatePriceRequest,
    GetOrderDetailByBatchNumRequest,
    GetPcbAuditInfoRequest,
    GetPcbWipProcessRequest,
    GetSteelPriceConfigRequest,
    GoodsCalculatePriceRequest,
    OrderDetailQueryRequest,
    OrderQueryRequest,
    OrderProcessQueryRequest,
    PcbCreateOrderRequest,
    UploadBlindViaHoleImgRequest,
    UploadGerberFileRequest,
    UploadRequest,
    UploadTdpFileRequest,
    TdpCreateOrderRequest,
    model_to_payload,
)


T = TypeVar("T")


@dataclass(slots=True)
class ApiResponse(Generic[T]):
    code: int
    message: str
    data: T | None
    status_code: int
    request_id: str | None = None
    headers: dict[str, str] = field(default_factory=dict)
    raw: Any = None

    @property
    def is_successful(self) -> bool:
        return self.status_code == 200 and self.code == 200

    def raise_for_status(self) -> None:
        if self.is_successful:
            return
        raise JLCBusinessError(
            code=self.code,
            message=self.message,
            request_id=self.request_id,
            status_code=self.status_code,
        )


class _BaseService:
    def __init__(self, client: JLCPCBClient) -> None:
        self._client = client


class PCBClient(_BaseService):
    def upload_gerber_file(self, request: UploadGerberFileRequest) -> ApiResponse[str]:
        return self._client.send(request)

    def upload_blind_via_hole_img(
        self, request: UploadBlindViaHoleImgRequest
    ) -> ApiResponse[str]:
        return self._client.send(request)

    def get_impedance_template_setting_list(
        self, request: GetImpedanceTemplateSettingListRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)

    def get_online_calculate_price(
        self, request: GetOnlineCalculatePriceRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def create_order(self, request: PcbCreateOrderRequest) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def get_pcb_wip_process(
        self, request: GetPcbWipProcessRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)

    def get_order_detail_by_batch_num(
        self, request: GetOrderDetailByBatchNumRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def get_pcb_audit_info(
        self, request: GetPcbAuditInfoRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def get_steel_price_config(
        self, request: GetSteelPriceConfigRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)


class ComponentClient(_BaseService):
    def get_component_info(
        self, request: GetComponentInfoRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def get_component_library_list(
        self, request: ComponentListRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)

    def get_private_component_library(
        self, request: CustomerPrivateStockListRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)

    def get_component_detail_by_code(
        self, request: ComponentCodesQueryVO
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)


class TDPClient(_BaseService):
    def upload_tdp_file(self, request: UploadTdpFileRequest) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def file_analysis_result(
        self, request: FileAnalysisResultRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def calculation_goods_costs(
        self, request: GoodsCalculatePriceRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def create_order(self, request: TdpCreateOrderRequest) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def order_list(self, request: OrderQueryRequest) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def order_detail(
        self, request: OrderDetailQueryRequest
    ) -> ApiResponse[dict[str, Any]]:
        return self._client.send(request)

    def order_process(
        self, request: OrderProcessQueryRequest
    ) -> ApiResponse[list[dict[str, Any]]]:
        return self._client.send(request)


class JLCPCBClient:
    def __init__(
        self,
        auth: JLCAuth,
        *,
        timeout: float | tuple[float, float] = 30.0,
        session: requests.Session | None = None,
    ) -> None:
        self.auth = auth
        self.timeout = timeout
        self._session = session or requests.Session()
        self.pcb = PCBClient(self)
        self.components = ComponentClient(self)
        self.tdp = TDPClient(self)

    @classmethod
    def from_env(
        cls,
        *,
        prefix: str = "JLCPCB_",
        timeout: float | tuple[float, float] = 30.0,
        session: requests.Session | None = None,
    ) -> JLCPCBClient:
        return cls(JLCAuth.from_env(prefix=prefix), timeout=timeout, session=session)

    def send(self, request: ApiRequest) -> ApiResponse[Any]:
        url = f"{self.auth.endpoint.rstrip('/')}{request.uri}"
        if isinstance(request, UploadRequest):
            return self._send_upload(url, request)
        if request.method == "GET":
            payload = request.to_payload()
            return self._send_get(url, payload)
        payload = request.to_payload()
        return self._send_post(url, payload)

    def _json_dumps(self, payload: dict[str, Any]) -> str:
        return json.dumps(model_to_payload(payload), ensure_ascii=False, separators=(",", ":"))

    def _send_get(self, url: str, payload: dict[str, Any]) -> ApiResponse[Any]:
        prepared = self._session.prepare_request(
            requests.Request(
                "GET",
                url,
                params=payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        )
        prepared.headers["Authorization"] = self.auth.build_authorization_header(
            method="GET",
            url=prepared.url,
            body="",
        )
        return self._dispatch(prepared)

    def _send_post(self, url: str, payload: dict[str, Any]) -> ApiResponse[Any]:
        body = self._json_dumps(payload)
        prepared = self._session.prepare_request(
            requests.Request(
                "POST",
                url,
                data=body,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
        )
        prepared.headers["Authorization"] = self.auth.build_authorization_header(
            method="POST",
            url=prepared.url,
            body=body,
        )
        return self._dispatch(prepared)

    def _send_upload(self, url: str, request: UploadRequest) -> ApiResponse[Any]:
        file_path = request.resolved_file()
        if not file_path.exists():
            raise FileNotFoundError(f"upload file not found: {file_path}")
        meta = self._json_dumps(request.to_payload())
        file_name = request.resolved_file_name()
        content_type = mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        with file_path.open("rb") as handle:
            prepared = self._session.prepare_request(
                requests.Request(
                    "POST",
                    url,
                    data={"meta": meta},
                    files={"file": (file_name, handle, content_type)},
                )
            )
            prepared.headers["Authorization"] = self.auth.build_authorization_header(
                method="POST",
                url=prepared.url,
                body=meta,
            )
            return self._dispatch(prepared)

    def _dispatch(self, prepared: requests.PreparedRequest) -> ApiResponse[Any]:
        try:
            response = self._session.send(prepared, timeout=self.timeout)
        except requests.RequestException as exc:
            raise JLCTransportError(str(exc)) from exc
        return self._parse_response(response)

    def _parse_response(self, response: requests.Response) -> ApiResponse[Any]:
        request_id = response.headers.get("J-Trace-ID")
        headers = dict(response.headers)
        content_type = response.headers.get("Content-Type", "")
        raw_text = response.text
        payload: Any
        if raw_text:
            try:
                payload = response.json()
            except ValueError:
                if "application/json" in content_type.lower():
                    raise JLCProtocolError("response declared JSON but could not be decoded")
                payload = None
        else:
            payload = None

        if isinstance(payload, dict):
            code = int(payload.get("code", response.status_code))
            message = str(payload.get("message", response.reason))
            data = payload.get("data")
            return ApiResponse(
                code=code,
                message=message,
                data=data,
                status_code=response.status_code,
                request_id=request_id,
                headers=headers,
                raw=payload,
            )

        return ApiResponse(
            code=response.status_code,
            message=raw_text or response.reason,
            data=None,
            status_code=response.status_code,
            request_id=request_id,
            headers=headers,
            raw=payload if payload is not None else raw_text,
        )
