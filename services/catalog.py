import sys
from pathlib import Path

from _common import run

from fastapi import APIRouter, FastAPI

CURRENT_DIR = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().parent

routes = APIRouter()


the_app = FastAPI()


if __name__ == "__main__":
    run("catalog")
