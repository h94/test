class ExampleProvider:
    """範例資料存取層 - 不連接任何 DB，以假資料示範 Provider 用途。"""

    def __init__(self, send_msg) -> None:
        self.send_msg = send_msg

    async def get_items(self, category: str, keyword: str | None, is_active: bool, start_date: str | None, sort_by: str) -> list[dict]:
        """
        取得指定分類的項目列表（假資料範例，不連接 DB）。

        Args:
            category (str): 項目分類，例如 "books"、"movies"
            keyword (str | None): 搜尋關鍵字，None 表示不過濾
            is_active (bool): 是否只回傳啟用中的項目
            start_date (str | None): 建立日期起始（YYYY-MM-DD），None 表示不限制
            sort_by (str): 排序欄位

        Returns:
            list[dict]: 項目列表
        """
        items = [
            {"id": "item_001", "name": "範例項目 A", "category": category, "is_active": True,  "created_at": "2026-01-10", "priority": 3},
            {"id": "item_002", "name": "範例項目 B", "category": category, "is_active": False, "created_at": "2026-03-05", "priority": 7},
            {"id": "item_003", "name": "範例項目 C", "category": category, "is_active": True,  "created_at": "2026-05-20", "priority": 1},
        ]
        if keyword is not None:
            items = [item for item in items if keyword in item["name"]]
        if is_active:
            items = [item for item in items if item["is_active"]]
        if start_date is not None:
            items = [item for item in items if item["created_at"] >= start_date]
        if sort_by in ("name", "created_at", "priority"):
            items = sorted(items, key=lambda item: item[sort_by])
        return items

    async def create_item(self, category: str, name: str, description: str, tags: list[str], priority: int, is_public: bool) -> dict:
        """
        建立項目（假資料範例，不寫入 DB）。

        Args:
            category (str): 項目分類
            name (str): 項目名稱
            description (str): 項目描述
            tags (list[str]): 標籤列表
            priority (int): 優先層級
            is_public (bool): 是否公開顯示

        Returns:
            dict: 建立結果
        """
        return {
            "id": "item_new_001",
            "name": name,
            "category": category,
            "description": description,
            "tags": tags,
            "priority": priority,
            "is_public": is_public,
        }
