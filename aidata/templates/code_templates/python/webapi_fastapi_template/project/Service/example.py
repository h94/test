class ExampleService:
    """範例業務邏輯層 - 負責參數處理與流程組裝，從 provider 取得資料。"""

    def __init__(self, provider) -> None:
        self.provider = provider

    async def get_items(self, category: str, keyword: str | None, is_active: bool, start_date: str | None, sort_by: str, limit: int) -> list[dict]:
        """
        取得項目列表，套用過濾與排序後截取筆數。

        Args:
            category (str): 項目分類
            keyword (str | None): 搜尋關鍵字，None 表示不過濾
            is_active (bool): 是否只回傳啟用中的項目
            start_date (str | None): 建立日期起始（YYYY-MM-DD），None 表示不限制
            sort_by (str): 排序欄位
            limit (int): 最多回傳筆數

        Returns:
            list[dict]: 過濾與排序後的項目列表
        """
        items = await self.provider.example.get_items(category, keyword, is_active, start_date, sort_by)
        return items[:limit]

    async def create_item(self, category: str, name: str, description: str, tags: list[str], priority: int, is_public: bool) -> dict:
        """
        建立新項目。

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
        return await self.provider.example.create_item(category, name, description, tags, priority, is_public)
