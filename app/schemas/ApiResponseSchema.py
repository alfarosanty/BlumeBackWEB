from pydantic import BaseModel
from typing import Generic, List, Optional, TypeVar
import math

T = TypeVar("T")


class PagedResult(BaseModel, Generic[T]):
    items: List[T]
    totalItems: int
    pageNumber: int
    pageSize: int
    totalPages: int

    @classmethod
    def crear(cls, items: List[T], total: int, page_number: int, page_size: int) -> "PagedResult[T]":
        total_pages = math.ceil(total / page_size) if page_size > 0 else 1
        return cls(
            items=items,
            totalItems=total,
            pageNumber=page_number,
            pageSize=page_size,
            totalPages=total_pages,
        )


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: Optional[str] = None

    @classmethod
    def ok(cls, data: T) -> "ApiResponse[T]":
        return cls(success=True, data=data)

    @classmethod
    def error(cls, message: str) -> "ApiResponse[None]":
        return cls(success=False, data=None, message=message)
