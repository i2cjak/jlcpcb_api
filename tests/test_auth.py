from __future__ import annotations

from jlcpcb_api import JLCAuth


def test_authorization_header_matches_doc_sample() -> None:
    auth = JLCAuth(
        app_id="293992070061998081",
        access_key="b6713a535d56412f805afadd7e818455",
        secret_key="z0BWlikshimuyiwBsH1i2qwnzMb3j3kA",
    )
    header = auth.build_authorization_header(
        method="POST",
        url="https://open.jlcpcb.com/order/v1/createOrder",
        body='{"goodsId":100,"quantity":52,"createdTime":"2024-03-21 10:03:20"}',
        nonce="IZHEJYNIHYZIE8S0LLC0VWTPJVRRTO50",
        timestamp=1625208260,
    )
    assert (
        header
        == 'JOP appid="293992070061998081",accesskey="b6713a535d56412f805afadd7e818455",timestamp="1625208260",nonce="IZHEJYNIHYZIE8S0LLC0VWTPJVRRTO50",signature="sygwKhKBkLwHVv0c7D+a/A7JTEJjGH/kLugFKh16918="'
    )
