class ExampleService:
    """範例業務邏輯層 - 從 provider 取得資料後進行處理並寫回。"""

    def __init__(self, send_msg, provider) -> None:
        self.send_msg = send_msg
        self.provider = provider

    async def process(self, source: str) -> int:
        """
        從指定來源取得資料，套用業務規則後寫回。

        Args:
            source (str): 資料來源名稱

        Returns:
            int: 本次處理的筆數
        """
        records = await self.provider.example.fetch_data(source)
        processed_count = 0
        for record in records:
            result = {
                "id": record["id"],
                "processed_value": record["value"] * 2,
            }
            await self.provider.example.save_result(result)
            processed_count += 1
        return processed_count
