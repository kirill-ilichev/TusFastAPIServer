from typing import Type
from typing import Optional
from fastapi import FastAPI
from tusfastapiserver.routers.base_router import BaseRouter
from tusfastapiserver.routers.post_router import PostRouter
from tusfastapiserver.routers.patch_router import PatchRouter
from tusfastapiserver.routers.head_router import HeadRouter
from tusfastapiserver.routers.options_router import OptionsRouter
from tusfastapiserver.routers.delete_router import DeleteRouter
from tusfastapiserver.config import Config
from tusfastapiserver.config import TusExtension


def add_tus_routers(
    app: FastAPI,
    config: Optional[Config] = None,
    post_router_cls: Type[BaseRouter] = PostRouter,
    patch_router_cls: Type[BaseRouter] = PatchRouter,
    head_router_cls: Type[BaseRouter] = HeadRouter,
    options_router_cls: Type[BaseRouter] = OptionsRouter,
    delete_router_cls: Type[BaseRouter] = DeleteRouter,
):
    if config is None:
        config = Config()

    mandatory_routers = [
        post_router_cls,
        patch_router_cls,
        head_router_cls,
        options_router_cls,
    ]
    routers = []

    for router_cls in mandatory_routers:
        routers.append(router_cls(config=config))

    if TusExtension.TERMINATION in config.enabled_extensions:
        routers.append(delete_router_cls(config=config))

    for router in routers:
        app.include_router(router.get_router())
