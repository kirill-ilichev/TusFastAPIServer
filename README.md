
# tusfastapiserver

[![Coverage Status](https://coveralls.io/repos/github/kirill-ilichev/TusFastAPIServer/badge.svg?branch=main)](https://coveralls.io/github/kirill-ilichev/TusFastAPIServer?branch=main)

> **tusfastapiserver** is a FastAPI extension implementing the [Tus.io resumable upload protocol](http://www.tus.io/protocols/resumable-upload.html), allowing resumable file uploads for handling large file transfers with ease.

---

## Features

This library supports the following Tus.io protocol extensions:

| Extension   | `local-store` |
| ----------- |---------------|
| Creation    | ✅             |
| Creation With Upload | ❌             |
| Expiration  | ❌             |
| Checksum    | ❌             |
| Termination | ❌             |
| Concatenation | ❌             |

---

## Prerequisites

- Python 3.8+
- FastAPI

---

## Installation

Install the library from PyPI:

```bash
pip install tusfastapiserver
```

---

## Quick Start

### main.py

```python
from fastapi import FastAPI
from tusfastapiserver.routers import add_tus_routers
from tusfastapiserver.config import Config

app = FastAPI()

config = Config(
    file_path="/path/to/upload/files",  # path to local-stored files
    metadata_path="/path/to/store/metadata",  # path to local-stored metadata
    path_prefix="/files/"  # TUS router path prefix
)

add_tus_routers(app, config)
```

---

## Customization

The advantage of this library is the ability to fully customize any of its routers.

You can dive into the library and rewrite various parts to suit your needs flexibly.

### Want to add your custom header to the response from a `HEAD` request? Easy:

```python
from fastapi import Response

from tusfastapiserver.routers import add_tus_routers
from tusfastapiserver.routers import HeadRouter
from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.config import Config

app = ...

config = Config(...)


class CustomHeadRouter(HeadRouter):
    def _prepare_response(self, response: Response, metadata: UploadMetadata):
        response = super()._prepare_response(response, metadata)
        response.headers["MY-CUSTOM-HEADER"] = "value"
        return response


add_tus_routers(app, config, head_router_cls=CustomHeadRouter)
```

### Want to check a user's permissions before they upload a file? Also simple:

```python
from fastapi import Request, Response

from tusfastapiserver.routers import add_tus_routers
from tusfastapiserver.routers import PostRouter
from tusfastapiserver.config import Config

app = ...

config = Config(...)


class User:
    pass


class CustomPostRouter(PostRouter):
    @staticmethod
    def _get_user() -> User:
        return User()

    @staticmethod
    def _check_user_permissions(user: User) -> bool:
        return True

    async def handle(self, request: Request, response: Response):
        user = self._get_user()
        self._check_user_permissions(user)
        return await super().handle(request, response)


add_tus_routers(app, config, post_router_cls=CustomPostRouter)
```
