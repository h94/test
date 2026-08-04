class ExampleProvider:
    """範例資料存取層 - 不連接任何外部服務，以假資料示範 Provider 用途。"""

    def __init__(self, send_msg) -> None:
        self.send_msg = send_msg

    async def fetch_data(self, source: str) -> list[dict]:
        """
        從資料來源取得資料（假資料範例）。

        Args:
            source (str): 資料來源名稱，例如 "site_a"、"db_main"

        Returns:
            list[dict]: 資料列表，每筆包含 id, source, value
        """
        return [
            {"id": "record_001", "source": source, "value": 100},
            {"id": "record_002", "source": source, "value": 200},
            {"id": "record_003", "source": source, "value": 300},
        ]

    async def save_result(self, result: dict) -> None:
        """
        將處理結果寫入目標（假資料範例，不做實際寫入）。

        Args:
            result (dict): 要寫入的結果資料，例如 {"id": "record_001", "processed_value": 150}
        """
        self.send_msg(f"[ExampleProvider] save_result: {result}", level="Information")
