from typing import Generic, TypeVar

from pydantic import BaseModel, validator
from pydantic.generics import GenericModel

DataT = TypeVar("DataT")


class ErrorModel(BaseModel):
    code: int
    message: str


class Envelope(GenericModel, Generic[DataT]):
    data: DataT | None
    error: ErrorModel | None

    @validator("error", always=True)
    @classmethod
    def check_consistency(cls, v, values):
        if v is not None and values["data"] is not None:
            raise ValueError("must not provide both data and error")
        if v is None and values.get("data") is None:
            raise ValueError("must provide data or error")
        return v
