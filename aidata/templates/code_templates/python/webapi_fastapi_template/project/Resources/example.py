from typing import Annotated
from fastapi import APIRouter, Path, Query, Request
from pydantic import BaseModel, Field
from Service.example import ExampleService


class GetItemsArgs(BaseModel):
    """GET /api/example/{category} 的 query 參數"""
    keyword: str | None = Field(default=None, description="搜尋關鍵字，模糊比對項目名稱；不填則不過濾")
    is_active: bool = Field(default=True, description="是否只回傳啟用中的項目")
    start_date: str | None = Field(default=None, description="建立日期起始，格式 YYYY-MM-DD；不填則不限制", pattern=r"^\d{4}-\d{2}-\d{2}$")
    sort_by: str = Field(default="name", description="排序欄位，允許值：name、created_at、priority")
    limit: int = Field(default=10, ge=1, le=100, description="最多回傳筆數，範圍 1~100")


class CreateItemBody(BaseModel):
    """建立項目的請求 body"""
    name: str = Field(description="項目名稱", min_length=1, max_length=100)
    description: str = Field(default="", description="項目描述")
    tags: list[str] = Field(default_factory=list, description="標籤列表，例如 [\"新品\", \"推薦\"]")
    priority: int = Field(default=0, ge=0, le=10, description="優先層級，0（最低）~10（最高）")
    is_public: bool = Field(default=True, description="是否公開顯示此項目")


class ExampleRoutes:
    router = APIRouter(tags=["example"], responses={500: {"description": "Internal Server Error"}})

    @router.get("/api/example/{category}")
    async def get_items(request: Request, args: Annotated[GetItemsArgs, Query()], category: str = Path(description="項目分類，例如 books、movies")):
        """
        依分類取得項目列表，支援關鍵字搜尋、狀態過濾、日期區間與排序。
        """
        provider = request.app.state.provider
        return await ExampleService(provider).get_items(category, args.keyword, args.is_active, args.start_date, args.sort_by, args.limit)

    @router.post("/api/example/{category}")
    async def create_item(request: Request, body: CreateItemBody, category: str = Path(description="項目分類，例如 books、movies")):
        """
        在指定分類下建立新項目。
        """
        provider = request.app.state.provider
        return await ExampleService(provider).create_item(category, body.name, body.description, body.tags, body.priority, body.is_public)
