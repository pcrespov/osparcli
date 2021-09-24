import sys
from pathlib import Path

from libs.application import run

from fastapi import APIRouter, FastAPI

APP_NAME = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().stem


routes = APIRouter()


the_app = FastAPI(title=APP_NAME)


if __name__ == "__main__":
    run(APP_NAME)
