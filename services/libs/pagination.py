from math import ceil
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from fastapi import Query, Request
from pydantic import (
    AnyHttpUrl,
    BaseModel,
    Extra,
    Field,
    NonNegativeInt,
    PositiveInt,
    validator,
)
from pydantic.generics import GenericModel
from starlette.datastructures import URL

########################### MODELS ###########################

DEFAULT_NUMBER_OF_ITEMS_PER_PAGE = 20


class PageMetaInfoLimitOffset(BaseModel):
    limit: PositiveInt = DEFAULT_NUMBER_OF_ITEMS_PER_PAGE
    total: NonNegativeInt
    offset: NonNegativeInt = 0
    count: NonNegativeInt

    @validator("offset")
    @classmethod
    def check_offset(cls, v, values):
        if v > 0 and v >= values["total"]:
            raise ValueError(
                f"offset {v} cannot be equal or bigger than total {values['total']}, please check"
            )
        return v

    @validator("count")
    @classmethod
    def check_count(cls, v, values):
        if v > values["limit"]:
            raise ValueError(
                f"count {v} bigger than limit {values['limit']}, please check"
            )
        if v > values["total"]:
            raise ValueError(
                f"count {v} bigger than expected total {values['total']}, please check"
            )
        if "offset" in values and (values["offset"] + v) > values["total"]:
            raise ValueError(
                f"offset {values['offset']} + count {v} is bigger than allowed total {values['total']}, please check"
            )
        return v

    class Config:
        extra = Extra.forbid

        schema_extra = {
            "examples": [
                {"total": 7, "count": 4, "limit": 4, "offset": 0},
            ]
        }


class PageLinks(BaseModel):
    self: AnyHttpUrl
    first: AnyHttpUrl
    prev: Optional[AnyHttpUrl]
    next: Optional[AnyHttpUrl]
    last: AnyHttpUrl

    class Config:
        extra = Extra.forbid


ItemT = TypeVar("ItemT")

# FIXME: replace PageResponseLimitOffset
# FIXME: page envelope is inconstent since DataT != Page ??
class Page(GenericModel, Generic[ItemT]):
    meta: PageMetaInfoLimitOffset = Field(alias="_meta")
    links: PageLinks = Field(alias="_links")
    data: List[ItemT]

    @classmethod
    def create_obj(
        cls,
        data: List[Any],
        request_url: URL,
        total: int,
        limit: int,
        offset: int,
    ) -> Dict[str, Any]:
        last_page = ceil(total / limit) - 1
        return dict(
            _meta=PageMetaInfoLimitOffset(
                total=total, count=len(data), limit=limit, offset=offset
            ),
            _links=PageLinks(
                self=f"{request_url.replace_query_params(offset=offset, limit=limit)}",
                first=f"{request_url.replace_query_params(offset= 0, limit= limit)}",
                prev=f"{request_url.replace_query_params(offset= max(offset - limit, 0), limit= limit)}"
                if offset > 0
                else None,
                next=f"{request_url.replace_query_params(offset= min(offset + limit, last_page * limit), limit= limit)}"
                if offset < (last_page * limit)
                else None,
                last=f"{request_url.replace_query_params(offset= last_page * limit, limit= limit)}",
            ),
            data=data,
        )


########################### DEPENDENCIES ###########################


def init_pagination(item_cls: Type):
    PageType = Page[item_cls]

    def _get(
        request: Request,
        offset: PositiveInt = Query(
            0, description="index to the first item to return (pagination)"
        ),
        limit: int = Query(
            20,
            description="maximum number of items to return (pagination)",
            ge=1,
            le=50,
        ),
    ) -> PageType:
        empty_page: PageType = PageType.parse_obj(
            Page.create_obj([], request.url, total=0, limit=limit, offset=offset)
        )
        return empty_page

    return _get
