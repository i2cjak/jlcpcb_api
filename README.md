# JLCPCB API

Small Python client for JLCPCB's overseas OpenAPI, reverse-engineered from the Java SDK JARs in this repo.

It supports:

- JOP request signing with HMAC-SHA256
- PCB endpoints
- Component endpoints
- 3D printing (`tdp`) endpoints
- File uploads using the same `meta` + `file` multipart format as the Java SDK

## Install

```bash
pip install -e .
```

## Configure

You need a JLC OpenAPI app with permissions enabled for the APIs you want to call.

Required credentials:

- `app_id`
- `access_key`
- `secret_key`

Optional environment variables used by `JLCPCBClient.from_env()`:

- `JLCPCB_APP_ID`
- `JLCPCB_ACCESS_KEY`
- `JLCPCB_SECRET_KEY`
- `JLCPCB_ENDPOINT` default: `https://open.jlcpcb.com`
- `JLCPCB_CONTEXT_PATH`
- `JLCPCB_RSA_PUBLIC_KEY`
- `JLCPCB_RSA_PRIVATE_KEY`

## Example

```python
from jlcpcb_api import JLCAuth, JLCPCBClient, ComponentListRequest

client = JLCPCBClient(
    JLCAuth(
        app_id="YOUR_APP_ID",
        access_key="YOUR_ACCESS_KEY",
        secret_key="YOUR_SECRET_KEY",
    )
)

result = client.components.get_component_library_list(
    ComponentListRequest(currentPage=1, pageSize=10)
)

print(result.status_code, result.code, result.message)
print(result.data)
```

## Notes

- Business success is `code == 200`.
- HTTP `403` with `API insufficient permissions, access denied` means the app exists but is missing the required JLC API scope.
- Run tests with `pytest -q`.
