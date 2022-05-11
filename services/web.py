import sys
from pathlib import Path

from fastapi import APIRouter, FastAPI
from libs.application import run

APP_NAME = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().stem


routes = APIRouter()


the_app = FastAPI(title=APP_NAME)
the_app.state.healthy = True


@the_app.get("/health")
async def health():
    if the_app.state.healthy:
        return "healthy like a rose"
    raise ValueError("I am sick")


@the_app.get("/virus")
async def make_sick():
    the_app.state.healthy = False


@the_app.get("/vaccine")
async def make_healthy():
    the_app.state.healthy = True


if __name__ == "__main__":
    run(APP_NAME)
