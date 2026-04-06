from __future__ import annotations

from dataclasses import dataclass, field, fields, is_dataclass
from decimal import Decimal
from os import PathLike
from pathlib import Path
from typing import Any, ClassVar


def _transient_field(default: Any = None) -> Any:
    return field(default=default, metadata={"serialize": False})


def _normalize_scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        integral = value.to_integral_value()
        return int(value) if value == integral else float(value)
    if isinstance(value, Path):
        return str(value)
    return value


def model_to_payload(value: Any) -> Any:
    if is_dataclass(value):
        payload: dict[str, Any] = {}
        for data_field in fields(value):
            if data_field.metadata.get("serialize", True) is False:
                continue
            field_value = getattr(value, data_field.name)
            if field_value is None:
                continue
            payload[data_field.name] = model_to_payload(field_value)
        return payload
    if isinstance(value, list):
        return [model_to_payload(item) for item in value]
    if isinstance(value, tuple):
        return [model_to_payload(item) for item in value]
    if isinstance(value, dict):
        return {
            str(key): model_to_payload(item)
            for key, item in value.items()
            if item is not None
        }
    return _normalize_scalar(value)


@dataclass(slots=True, kw_only=True)
class ApiRequest:
    uri: ClassVar[str]
    method: ClassVar[str] = "POST"

    def to_payload(self) -> dict[str, Any]:
        return model_to_payload(self)


@dataclass(slots=True, kw_only=True)
class GetRequest(ApiRequest):
    method: ClassVar[str] = "GET"


@dataclass(slots=True, kw_only=True)
class PostRequest(ApiRequest):
    method: ClassVar[str] = "POST"


@dataclass(slots=True, kw_only=True)
class UploadRequest(ApiRequest):
    method: ClassVar[str] = "POST"
    file: str | PathLike[str] = field(metadata={"serialize": False})
    fileName: str | None = _transient_field()

    def resolved_file(self) -> Path:
        return Path(self.file).expanduser().resolve()

    def resolved_file_name(self) -> str:
        return self.fileName or self.resolved_file().name


@dataclass(slots=True, kw_only=True)
class FileData:
    fileStoreId: str | None = None
    fileName: str | None = None


@dataclass(slots=True, kw_only=True)
class OrderAddressData:
    firstName: str | None = None
    lastName: str | None = None
    companyName: str | None = None
    streetAddress: str | None = None
    addressLine2: str | None = None
    city: str | None = None
    country: str | None = None
    province: str | None = None
    postalCode: str | None = None
    cellOrMobileNumber: str | None = None


@dataclass(slots=True, kw_only=True)
class PcbBlindViaHoleData:
    index: int | None = None
    holeAttribute: int | None = None
    layerLevel: int | None = None
    holeDepth: Decimal | None = None
    customerRemark: str | None = None
    fileInfoList: list[FileData] | None = None


@dataclass(slots=True, kw_only=True)
class PcbOrderServiceCraftData:
    serviceConfigCode: str | None = None
    serviceConfigShow: str | None = None
    configOptionShow: str | None = None


@dataclass(slots=True, kw_only=True)
class SerialQrCodeConfigData:
    qrCodeFormat: int | None = None
    qrLocation: int | None = None
    prefixCode: str | None = None
    addUniqueCode: bool | None = None
    incrCode: str | None = None


@dataclass(slots=True, kw_only=True)
class PcbOrderCraftData:
    layer: int | None = None
    width: float | None = None
    length: float | None = None
    qty: int | None = None
    thickness: float | None = None
    pcbColor: int | None = None
    surfaceFinish: int | None = None
    copperWeight: Decimal | None = None
    insideCuprumThickness: str | None = None
    goldFinger: int | None = None
    materialDetails: int | None = None
    panelFlag: int | None = None
    panelByJLCPCB_X: int | None = None
    panelByJLCPCB_Y: int | None = None
    differentDesign: int | None = None
    flyingProbeTest: int | None = None
    castellatedHoles: int | None = None
    orderDetailsRemark: str | None = None
    cascadeStructure: int | None = None
    impedanceTemplateCode: str | None = None
    impedanceFlag: str | None = None
    isAddCustomerCode: str | None = None
    plateType: int | None = None
    autoConfirmProductionFile: bool | None = None
    markOnPcb: int | None = None
    viaCovering: int | None = None
    needTechnics: int | None = None
    technicsSize: int | None = None
    goldThickness: Decimal | None = None
    edgeRounding: bool | None = None
    rowSpacing: Decimal | None = None
    columnSpacing: Decimal | None = None
    serialQrCodeConfigData: SerialQrCodeConfigData | None = None
    edaSoftware: str | None = None
    fpcGoldFingerThickness: Decimal | None = None
    serviceConfigVos: list[PcbOrderServiceCraftData] | None = None
    pcbBlindViaHoleInfoDTOList: list[PcbBlindViaHoleData] | None = None


@dataclass(slots=True, kw_only=True)
class SteelOrderCraftData:
    dimensionsID: int | None = None
    stencilQty: int | None = None
    electropolishing: int | None = None
    fiducials: int | None = None
    steelPurpose: str | None = None
    customizeFlag: int | None = None
    customizeSizeX: int | None = None
    customizeSizeY: int | None = None
    stencilSide: int | None = None
    orderRemark: str | None = None
    confirmFile: bool | None = None
    autoConfirmProductionFile: int | None = None
    moreShapeFlag: bool | None = None


@dataclass(slots=True, kw_only=True)
class GetImpedanceTemplateSettingListRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/getImpedanceTemplateSettingList"
    stencilLayer: int | None = None
    stencilPly: Decimal | None = None
    cuprumThickness: Decimal | None = None
    insideCuprumThickness: Decimal | None = None
    plateType: int | None = None
    delamination: bool | None = None


@dataclass(slots=True, kw_only=True)
class GetOnlineCalculatePriceRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/calculate"
    orderType: int | None = None
    pcbParam: PcbOrderCraftData | None = None
    smtStencilParam: SteelOrderCraftData | None = None
    achieveDate: int | None = None
    country: str | None = None
    postCode: str | None = None
    city: str | None = None
    fileKey: str | None = None
    batchNum: str | None = None
    shippingMethod: str | None = None


@dataclass(slots=True, kw_only=True)
class GetOrderDetailByBatchNumRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/order/detail"
    batchNum: str | None = None


@dataclass(slots=True, kw_only=True)
class GetPcbAuditInfoRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/audit/get"
    key: str | None = None
    language: int | None = None


@dataclass(slots=True, kw_only=True)
class GetPcbWipProcessRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/wip/get"
    orderUUID: str | None = None


@dataclass(slots=True, kw_only=True)
class GetSteelPriceConfigRequest(GetRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/getSteelPriceConfig"


@dataclass(slots=True, kw_only=True)
class PcbCreateOrderRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/create"
    fileKey: str | None = None
    batchNum: str | None = None
    shippingAddress: OrderAddressData | None = None
    billingAddress: OrderAddressData | None = None
    TaxOrVATNumber: str | None = None
    billingAddressFlag: int | None = None
    orderType: int | None = None
    pcbParam: PcbOrderCraftData | None = None
    smtStencilParam: SteelOrderCraftData | None = None
    achieveDate: int | None = None
    shippingMethod: str | None = None


@dataclass(slots=True, kw_only=True)
class UploadBlindViaHoleImgRequest(UploadRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/uploadBlindViaHoleImg"


@dataclass(slots=True, kw_only=True)
class UploadGerberFileRequest(UploadRequest):
    uri: ClassVar[str] = "/overseas/openapi/pcb/uploadGerber"


@dataclass(slots=True, kw_only=True)
class ComponentCodesQueryVO(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/component/getComponentDetailByCode"
    componentCodes: list[str] | None = None


@dataclass(slots=True, kw_only=True)
class ComponentListRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/component/getComponentLibraryList"
    currentPage: int | None = 1
    pageSize: int | None = 30


@dataclass(slots=True, kw_only=True)
class CustomerPrivateStockListRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/component/getPrivateComponentLibrary"
    currentPage: int | None = 1
    pageSize: int | None = 30


@dataclass(slots=True, kw_only=True)
class GetComponentInfoRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/component/getComponentInfos"
    lastKey: str | None = None


@dataclass(slots=True, kw_only=True)
class CraftAttributeShoppingCart:
    craftAttributeAccessId: str | None = None
    customerCraft: str | None = None
    resourceUrl: str | None = None


@dataclass(slots=True, kw_only=True)
class CraftShoppingCart:
    craftAccessId: str | None = None
    attributes: list[CraftAttributeShoppingCart] | None = None


@dataclass(slots=True, kw_only=True)
class CustomerAddress:
    uuid: str | None = None
    orderType: str | None = None
    country: str | None = None
    city: str | None = None
    state: str | None = None
    street: str | None = None
    street2: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    phone: str | None = None
    postcode: str | None = None
    type: str | None = None
    companyName: str | None = None
    defaultAddress: bool | None = None
    defaultChecked: bool | None = None
    brazilCpnj: str | None = None
    taxVat: str | None = None
    eoriNo: str | None = None
    partitionName: str | None = None
    areaCode: str | None = None
    commercialRegistrationId: str | None = None
    vatCheckFlag: bool | None = None
    shortAddress: str | None = None
    certificateCode: str | None = None


@dataclass(slots=True, kw_only=True)
class FileAnalysisResultRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/file/result"
    fileAccessId: str | None = None


@dataclass(slots=True, kw_only=True)
class GoodsCalculatePriceRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/calculate"
    materialAccessId: str | None = None
    materialColorAccessId: str | None = None
    modelAccessId: str | None = None
    fileAccessId: str | None = None
    fileName: str | None = None
    itemName: str | None = None
    itemPrice: Decimal | None = None
    itemCount: int | None = None
    surfaceTreatmentProcess: int | None = None
    materialDeliveryAccessId: str | None = None
    goodsUsefulness: str | None = None
    goodsCustomsType: int | None = None
    customerRemarks: str | None = None
    craftShoppingCartDTOList: list[CraftShoppingCart] | None = None
    shippingAddress: CustomerAddress | None = None
    freightMode: str | None = None


@dataclass(slots=True, kw_only=True)
class OrderDetailQueryRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/order/detail"
    batchNum: str | None = None


@dataclass(slots=True, kw_only=True)
class OrderProcessQueryRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/order/process"
    orderNo: str | None = None


@dataclass(slots=True, kw_only=True)
class OrderQueryRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/order/list"
    currentPage: int | None = None
    pageRows: int | None = None
    businessType: int | None = None
    businessTypeStr: str | None = None
    orderBusinessSystemType: int | None = None
    searchKey: str | None = None
    orderStatus: int | None = None
    batchStatus: str | None = None
    fromType: int | None = None
    orderNum: str | None = None
    orderStatisticsType: int | None = None
    waitPayOrSupplement: bool | None = None
    waitBizConfirm: bool | None = None
    prevBatchNum: str | None = None


@dataclass(slots=True, kw_only=True)
class TdpCreateOrderRequest(PostRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/order/create"
    materialAccessId: str | None = None
    materialColorAccessId: str | None = None
    modelAccessId: str | None = None
    fileAccessId: str | None = None
    fileName: str | None = None
    itemName: str | None = None
    itemPrice: Decimal | None = None
    itemCount: int | None = None
    surfaceTreatmentProcess: int | None = None
    materialDeliveryAccessId: str | None = None
    goodsUsefulness: str | None = None
    goodsCustomsType: int | None = None
    customerRemarks: str | None = None
    craftShoppingCartDTOList: list[CraftShoppingCart] | None = None
    shippingAddress: CustomerAddress | None = None
    freightMode: str | None = None
    billingAddress: CustomerAddress | None = None
    billingUseShippingAddressFlag: bool | None = None
    typeOfTrade: int | None = None
    batchNum: str | None = None


@dataclass(slots=True, kw_only=True)
class UploadTdpFileRequest(UploadRequest):
    uri: ClassVar[str] = "/overseas/openapi/tdp/api/upload"
