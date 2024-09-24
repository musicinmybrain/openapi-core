---
hide:
  - navigation
---

# openapi-core

Openapi-core is a Python library that adds client-side and server-side support
for the [OpenAPI v3.0](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.3.md)
and [OpenAPI v3.1](https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md) specification.

## Key features

- [Validation](validation.md) and [Unmarshalling](unmarshalling.md) of request and response data (including webhooks)
- [Integrations](integrations/index.md) with popular libraries (Requests, Werkzeug) and frameworks (Django, Falcon, Flask, Starlette)
- [Customization](customizations/index.md) with **media type deserializers** and **format unmarshallers**
- [Security](security.md) data providers (API keys, Cookie, Basic and Bearer HTTP authentications)

## Installation

=== "Pip + PyPI (recommented)"

    ``` console
    pip install openapi-core
    ```

=== "Pip + the source"

    ``` console
    pip install -e git+https://github.com/python-openapi/openapi-core.git#egg=openapi_core
    ```

## First steps

Firstly create your OpenAPI object.

```python
from openapi_core import OpenAPI

openapi = OpenAPI.from_file_path('openapi.json')
```

Now you can use it to validate and unmarshal your requests and/or responses.

```python
# raises error if request is invalid
result = openapi.unmarshal_request(request)
```

Retrieve validated and unmarshalled request data

```python
# get parameters
path_params = result.parameters.path
query_params = result.parameters.query
cookies_params = result.parameters.cookies
headers_params = result.parameters.headers
# get body
body = result.body
# get security data
security = result.security
```

Request object should implement OpenAPI Request protocol. Check [Integrations](integrations/index.md) to find oficially supported implementations.

For more details read about [Unmarshalling](unmarshalling.md) process.

If you just want to validate your request/response data without unmarshalling, read about [Validation](validation.md) instead.

## Related projects

- [openapi-spec-validator](https://github.com/python-openapi/openapi-spec-validator)
  : Python library that validates OpenAPI Specs against the OpenAPI 2.0 (aka Swagger), OpenAPI 3.0 and OpenAPI 3.1 specification. The validator aims to check for full compliance with the Specification.
- [openapi-schema-validator](https://github.com/python-openapi/openapi-schema-validator)
  : Python library that validates schema against the OpenAPI Schema Specification v3.0 and OpenAPI Schema Specification v3.1.

## License

The project is under the terms of BSD 3-Clause License.