from typing import Optional

from fastapi import Response
from fastapi import status

from tusfastapiserver.config import Config

from tusfastapiserver.routers import BaseRouter
from tusfastapiserver.exceptions import FileNotFoundException
from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.utils.metadata import stringify


class HeadRouter(BaseRouter):
    def __init__(self, config: Optional[Config] = None, dependencies=None):
        config = config or Config()
        super().__init__(config, dependencies)
        self.add_route("HEAD")

    def _get_router_path(self) -> str:
        return self.config.head_router_path

    async def handle(self, file_id: str, response: Response):
        self._validate_file_id(file_id)
        metadata = self.metadata_strategy.get_metadata(file_id)
        response = self._prepare_response(response, metadata)
        return response

    def _validate_file_id(self, file_id: str):
        if not self.metadata_strategy.is_metadata_exists(file_id):
            raise FileNotFoundException()

        if not self.storage_strategy.is_file_exists(file_id):
            raise FileNotFoundException()

    def _prepare_response(self, response: Response, metadata: UploadMetadata):
        response.headers["Upload-Offset"] = str(metadata.upload_offset)
        response.headers["Cache-Control"] = "no-store"
        if not metadata.upload_length:
            response.headers["Upload-Defer-Length"] = "1"
        else:
            response.headers["Upload-Length"] = str(metadata.upload_length)

        if metadata.metadata:
            response.headers["Upload-Metadata"] = stringify(metadata.metadata)
        response.status_code = status.HTTP_200_OK
        return response
