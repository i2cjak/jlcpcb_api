<p align="center">
  <img src="img/jlcpcb_api.png" alt="JLC API Platform" width="900" />
</p>

<p align="center">
  Simple Python client for JLCPCB's overseas OpenAPI, reverse-engineered from the Java SDK JARs.
</p>

## Install

```bash
git clone https://github.com/i2cjak/jlcpcb_api
cd jlcpcb_api
```

### uv

```bash
uv sync
```

or:

```bash
uv pip install -e .
```

### pip

```bash
pip install -e .
```

## Configure

You need a JLC OpenAPI app with:

- `app_id`
- `access_key`
- `secret_key`
- the required API permissions enabled in JLC's console

Optional env vars for `JLCPCBClient.from_env()`:

- `JLCPCB_APP_ID`
- `JLCPCB_ACCESS_KEY`
- `JLCPCB_SECRET_KEY`
- `JLCPCB_ENDPOINT`
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
- `403 API insufficient permissions, access denied` means the app exists but is missing JLC API scope.
- Run tests with `pytest -q` or `uv run pytest -q`.
