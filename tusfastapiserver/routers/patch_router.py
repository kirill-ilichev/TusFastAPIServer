from typing import Optional
import logging

from fastapi import Request
from fastapi import Response
from fastapi import status

from tusfastapiserver.exceptions import InvalidContentTypeException
from tusfastapiserver.exceptions import MissingContentTypeException
from tusfastapiserver.exceptions import FileNotFoundException
from tusfastapiserver.exceptions import MissingUploadOffsetException
from tusfastapiserver.exceptions import InvalidUploadOffsetException
from tusfastapiserver.exceptions import InvalidUploadLengthException
from tusfastapiserver.exceptions import MismatchUploadOffsetException
from tusfastapiserver.routers import BaseRouter
from tusfastapiserver.config import Config
from tusfastapiserver.schemas import UploadMetadata

logger = logging.getLogger(__name__)


class PatchRouter(BaseRouter):
    def __init__(self, config: Optional[Config] = None, dependencies=None):
        config = config or Config()
        super().__init__(config, dependencies)
        self.add_route("PATCH")

    def _get_router_path(self) -> str:
        return self.config.patch_router_path

    async def handle(
        self, file_id: str, request: Request, response: Response
    ):
        logger.info(f"Handling PATCH request for file_id: {file_id}")
        self._validate_file_id(file_id)
        self._validate_headers(request)
        metadata = self.metadata_strategy.get_metadata(file_id)
        self._compare_headers_with_metadata(request, metadata)
        if request.headers.get("upload-length"):
            metadata.upload_length = int(request.headers.get("upload-length"))
            self.metadata_strategy.update(metadata)
        async for chunk in request.stream():
            self.storage_strategy.update(metadata, chunk)
            metadata.upload_offset += len(chunk)
            self.metadata_strategy.update(metadata)
        response = self._prepare_response(response, metadata)
        logger.info(f"PATCH request for file_id: {file_id} completed successfully")
        return response

    def _validate_headers(self, request: Request):
        logger.debug("Validating headers")
        self._validate_content_type(request.headers.get("content-type"))
        self._validate_upload_offset(request.headers.get("upload-offset"))
        self._validate_upload_length(request.headers.get("upload-length"))

    @staticmethod
    def _validate_content_type(content_type: Optional[str]):
        logger.debug(f"Validating content type: {content_type}")
        if not content_type:
            raise MissingContentTypeException()
        if content_type != "application/offset+octet-stream":
            logger.error("Invalid content type")
            raise InvalidContentTypeException()

    def _validate_file_id(self, file_id: str):
        logger.debug(f"Validating file_id: {file_id}")
        if not self.metadata_strategy.is_metadata_exists(file_id):
            logger.error("Metadata not found for file_id")
            raise FileNotFoundException()

        if not self.storage_strategy.is_file_exists(file_id):
            logger.error("File not found for file_id")
            raise FileNotFoundException()

    @staticmethod
    def _validate_upload_offset(upload_offset: Optional[str]):
        logger.debug(f"Validating upload offset: {upload_offset}")
        if upload_offset is None:
            logger.error("Missing upload offset")
            raise MissingUploadOffsetException()

        if not upload_offset.isdigit():
            logger.error("Invalid upload offset")
            raise InvalidUploadOffsetException()

        if int(upload_offset) < 0:
            logger.error("Negative upload offset")
            raise InvalidUploadOffsetException()

    @staticmethod
    def _validate_upload_length(upload_length: Optional[str]):
        logger.debug(f"Validating upload length: {upload_length}")
        if upload_length is None:
            return

        if not upload_length.isdigit():
            logger.error("Invalid upload length")
            raise InvalidUploadLengthException()

        if int(upload_length) < 0:
            logger.error("Negative upload length")
            raise InvalidUploadLengthException()

    def _compare_headers_with_metadata(
        self, request: Request, metadata: UploadMetadata
    ):
        logger.debug("Comparing headers with metadata")
        self._compare_upload_offset_with_metadata(
            request.headers["upload-offset"], metadata
        )
        self._compare_upload_length_with_metadata(
            request.headers.get("upload-length"), metadata
        )

    @staticmethod
    def _compare_upload_offset_with_metadata(
        upload_offset: str, metadata: UploadMetadata
    ):
        logger.debug(f"Comparing upload offset: {upload_offset} with metadata offset: {metadata.upload_offset}")
        if int(upload_offset) != metadata.upload_offset:
            logger.error("Mismatch upload offset")
            raise MismatchUploadOffsetException()

    @staticmethod
    def _compare_upload_length_with_metadata(
        upload_length: Optional[str], metadata: UploadMetadata
    ):
        logger.debug(f"Comparing upload length: {upload_length} with metadata length: {metadata.upload_length}")
        if upload_length is not None:
            if not upload_length.isdigit():
                raise InvalidUploadLengthException()
            if metadata.upload_length is not None:
                raise InvalidUploadLengthException()
            if int(upload_length) < metadata.upload_offset:
                raise InvalidUploadLengthException()

    def _prepare_response(self, response: Response, metadata: UploadMetadata):
        logger.debug("Preparing response")
        response.headers["Upload-Offset"] = str(metadata.upload_offset)
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
