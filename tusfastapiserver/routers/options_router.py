from typing import Optional

from tusfastapiserver.routers import BaseRouter
from tusfastapiserver.config import Config


class OptionsRouter(BaseRouter):
    def __init__(self, config: Optional[Config] = None, dependencies=None):
        config = config or Config()
        super().__init__(config, dependencies)
        self.add_route("OPTIONS")

    def _get_router_path(self) -> str:
        return self.config.options_router_path
