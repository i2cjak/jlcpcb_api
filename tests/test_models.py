from __future__ import annotations

from decimal import Decimal

from jlcpcb_api import OrderAddressData, PcbCreateOrderRequest, PcbOrderCraftData


def test_model_serialization_omits_none_fields_and_keeps_nested_keys() -> None:
    request = PcbCreateOrderRequest(
        fileKey="file-key",
        orderType=1,
        shippingAddress=OrderAddressData(firstName="Ada", country="US"),
        pcbParam=PcbOrderCraftData(
            layer=2,
            qty=5,
            rowSpacing=Decimal("0.25"),
        ),
    )

    payload = request.to_payload()

    assert "billingAddress" not in payload
    assert payload["shippingAddress"] == {"firstName": "Ada", "country": "US"}
    assert payload["pcbParam"]["layer"] == 2
    assert payload["pcbParam"]["qty"] == 5
    assert payload["pcbParam"]["rowSpacing"] == 0.25
