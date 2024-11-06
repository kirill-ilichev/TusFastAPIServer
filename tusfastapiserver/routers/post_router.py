import uuid
import logging
from typing import Optional

from fastapi import Request
from fastapi import Response
from fastapi import status

from tusfastapiserver import TUS_RESUMABLE
from tusfastapiserver.routers import BaseRouter
from tusfastapiserver.config import Config
from tusfastapiserver.exceptions import InvalidContentTypeException
from tusfastapiserver.exceptions import InvalidUploadDeferLengthException
from tusfastapiserver.exceptions import InvalidTusResumableException
from tusfastapiserver.exceptions import MissingUploadLengthException
from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.utils.metadata import parse as parse_metadata

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TODO: add upload-concat support
# TODO: add support for Creation With Upload
class PostRouter(BaseRouter):
    def __init__(self, config: Optional[Config] = None, dependencies=None):
        config = config or Config()
        super().__init__(config, dependencies)
        self.add_route("POST")
        logger.info("PostRouter initialized with POST route.")

    def _get_router_path(self) -> str:
        path = self.config.post_router_path
        logger.debug(f"Router path: {path}")
        return path

    async def handle(self, request: Request, response: Response):
        logger.info("Handling request.")
        self._validate_headers(request)
        upload_metadata = self._create_upload_metadata(request)
        self.storage_strategy.initialize(upload_metadata)
        self.metadata_strategy.initialize(upload_metadata)
        response = self._prepare_response(response, request, upload_metadata)
        logger.info("Request handled successfully.")
        return response

    def _validate_headers(self, request: Request):
        logger.debug("Validating headers.")
        self._validate_tus_resumable(request.headers.get("tus-resumable"))
        self._validate_length_headers(
            request.headers.get("upload-length"),
            request.headers.get("upload-defer-length"),
        )
        self._validate_content_type(request.headers.get("content-type"))
        self._validate_metadata(request.headers.get("upload-metadata"))
        logger.debug("Headers validated.")

    @staticmethod
    def _validate_tus_resumable(tus_resumable: Optional[str]):
        if tus_resumable is None:
            logger.error("Missing 'tus-resumable' header.")
            raise InvalidTusResumableException()

    @staticmethod
    def _validate_length_headers(
        upload_length: Optional[str], upload_defer_length: Optional[str]
    ):
        if upload_length is None and upload_defer_length is None:
            raise MissingUploadLengthException()
        if upload_defer_length and not upload_defer_length.isdigit():
            raise InvalidUploadDeferLengthException()

    @staticmethod
    def _validate_content_type(content_type: Optional[str]):
        if content_type and content_type != "application/offset+octet-stream":
            logger.error(f"Invalid content type: {content_type}")
            raise InvalidContentTypeException()

    @staticmethod
    def _validate_metadata(metadata: Optional[str]):
        if metadata is not None:
            logger.debug("Parsing metadata.")
            parse_metadata(metadata)

    def _create_upload_metadata(self, request: Request) -> UploadMetadata:
        logger.debug("Creating upload metadata.")
        file_id = str(uuid.uuid4())
        tus_resumable = request.headers["tus-resumable"]
        upload_length = request.headers.get("upload-length")
        upload_defer_length = request.headers.get("upload-defer-length")
        metadata = parse_metadata(request.headers.get("upload-metadata"))
        upload_storage_path = self.storage_strategy.generate_file_path(file_id)
        upload_metadata_path = self.metadata_strategy.generate_metadata_path(file_id)
        upload_metadata = UploadMetadata(
            id=file_id,
            tus_resumable=tus_resumable,
            upload_length=int(upload_length) if upload_length is not None else None,
            upload_defer_length=(
                bool(upload_defer_length) if upload_defer_length is not None else None
            ),
            metadata=metadata,
            storage_strategy_type=self.storage_strategy.storage_strategy_type,
            metadata_strategy_type=self.metadata_strategy.metadata_strategy_type,
            upload_storage_path=upload_storage_path,
            upload_metadata_path=upload_metadata_path,
        )
        logger.info(f"Upload metadata created for file ID: {file_id}")
        return upload_metadata

    def _prepare_response(
        self, response: Response, request: Request, upload_metadata: UploadMetadata
    ) -> Response:
        logger.debug("Preparing response.")
        response.status_code = status.HTTP_201_CREATED
        response.headers["Location"] = self._get_location(request, upload_metadata)
        response.headers["Tus-Resumable"] = TUS_RESUMABLE
        logger.debug("Response prepared.")
        return response
