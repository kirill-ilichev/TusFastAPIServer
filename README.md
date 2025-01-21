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