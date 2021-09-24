import sys
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from libs.application import run
from libs.envelope import Envelope
from libs.pagination import Page, init_pagination
from pydantic import BaseModel

APP_NAME = Path(sys.argv[0] if __name__ == "__main__" else __file__).resolve().stem

UserId = int


class UserNew(BaseModel):
    name: str


class User(BaseModel):
    name: str


class UserDetail(BaseModel):
    address: str


class UserUpdate(BaseModel):
    pass


def get_valid_user(user_id: UserId) -> UserId:
    if not user_id:  # TODO: check
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project does not exists"
        )

    return user_id


######################################################################################################

routes = APIRouter(prefix="/users", tags=["users"])


@routes.get("", response_model=Page[User])
def list_users(page=Depends(init_pagination(User))):
    ...


@routes.post(
    "", response_model=Envelope[UserDetail], status_code=status.HTTP_201_CREATED
)
def create_user(user: UserNew):
    ...


@routes.get("/{user_id}", response_model=Envelope[UserDetail])
def get_user(user_id: UserId = Depends(get_valid_user)):
    ...


@routes.put("/{user_id}", response_model=Envelope[UserDetail])
def replace_user(user: UserNew, user_id: UserId = Depends(get_valid_user)):
    ...


@routes.patch("/{user_id}", response_model=Envelope[UserDetail])
def update_user(user: UserUpdate, user_id: UserId = Depends(get_valid_user)):
    ...


@routes.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user(user_id: UserId = Depends(get_valid_user)):
    ...


the_app = FastAPI(title=APP_NAME)
the_app.include_router(routes)


if __name__ == "__main__":
    run(APP_NAME)
