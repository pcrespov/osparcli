import sys
from pathlib import Path
from types import FunctionType
from typing import Any, Callable, Dict, List

import uvicorn
from fastapi import APIRouter, FastAPI
from fastapi.routing import APIRoute
from starlette.requests import Request

CURRENT_FILE = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve()
SERVICES_DIR = CURRENT_FILE.parent.parent


def run(app_name: str):
    uvicorn.run(
        f"{app_name}:the_app",
        host="0.0.0.0",
        reload=True,
        reload_dirs=[str(SERVICES_DIR)],
        log_level="debug",
    )


def redefine_operation_id_in_router(router: APIRouter, operation_id_prefix: str):
    # TODO: use servicelib.fastapi.openapi instead
    for route in router.routes:
        if isinstance(route, APIRoute):
            assert isinstance(route.endpoint, FunctionType)  # nosec
            route.operation_id = (
                f"{operation_id_prefix}._{route.endpoint.__name__}_handler"
            )


def get_reverse_url_mapper(request: Request) -> Callable:
    def reverse_url_mapper(name: str, **path_params: Any) -> str:
        return request.url_for(name, **path_params)

    return reverse_url_mapper
