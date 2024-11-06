from fastapi import APIRouter
from fastapi import Request
from fastapi import Response

from tusfastapiserver.schemas import UploadMetadata
from tusfastapiserver.config import Config
from tusfastapiserver.config import StorageStrategyType
from tusfastapiserver.config import MetadataStrategyType
from tusfastapiserver.storages import LocalStorageStrategy
from tusfastapiserver.metadata import LocalMetadataStrategy


STORAGE_STRATEGY_MAP = {
    StorageStrategyType.LOCAL: LocalStorageStrategy,
}

METADATA_STRATEGY_MAP = {
    MetadataStrategyType.LOCAL: LocalMetadataStrategy,
}


class BaseRouter:
    def __init__(self, config: Config, dependencies=None) -> None:
        self.config = config
        self.router = APIRouter(dependencies=dependencies or [])
        self._storage_strategy = STORAGE_STRATEGY_MAP[config.storage_strategy_type](
            config
        )
        self._metadata_strategy = METADATA_STRATEGY_MAP[config.metadata_strategy_type](
            config
        )

    async def handle(self, *args, **kwargs):
        raise NotImplementedError()

    def _get_router_path(self) -> str:
        raise NotImplementedError()

    def _prepare_response(self, *args, **kwargs):
        raise NotImplementedError()

    def get_router(self) -> APIRouter:
        return self.router

    def add_route(self, method: str, *args, **kwargs):
        self.router.add_api_route(
            path=self._get_router_path(),
            endpoint=self.handle,
            methods=[method],
        )

    @property
    def storage_strategy(self):
        return self._storage_strategy

    @storage_strategy.setter
    def storage_strategy(self, storage_strategy):
        self._storage_strategy = storage_strategy(self.config)

    @property
    def metadata_strategy(self):
        return self._metadata_strategy

    @metadata_strategy.setter
    def metadata_strategy(self, metadata_strategy):
        self._metadata_strategy = metadata_strategy(self.config)

    @staticmethod
    def _get_host_and_proto(request: Request) -> tuple:
        proto = "http"
        host = request.headers.get("host")
        if request.headers.get("X-Forwarded-Proto") is not None:
            proto = request.headers["X-Forwarded-Proto"]
        if request.headers.get("X-Forwarded-Host") is not None:
            host = request.headers["X-Forwarded-Host"]
        return proto, host

    def _get_location(self, request: Request, upload_metadata: UploadMetadata) -> str:
        proto, host = self._get_host_and_proto(request)
        return f"{proto}://{host}{self.config.path_prefix}/{upload_metadata.id}"
