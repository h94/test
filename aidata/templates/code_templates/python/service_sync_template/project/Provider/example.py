from TCZB.Datetime import UnixNow


class ExampleProvider:
    """
    範例 Provider：封裝 Cassandra 讀寫／外部 HTTP，僅負責資料 IO。
    session 由 __main__.py 建立後注入；未連線時以假資料示範查詢／寫回流程。
    """

    def __init__(self, send_msg, session=None) -> None:
        self.send_msg = send_msg
        self.session = session

    def fetch_pending_items(self, limit=100):
        """查詢待處理項目（範例以假資料模擬 Cassandra SELECT）。"""
        try:
            if self.session:
                # rows = self.session.execute("SELECT ... LIMIT %s", (limit,))
                pass
            return [
                {"item_id": "G001", "status": "pending", "amount": 100},
                {"item_id": "G002", "status": "pending", "amount": 250},
            ][:limit]
        except Exception as error:
            error_msg = f"fetch_pending_items failed: {error}"
            self.send_msg(error_msg, level="Error")
            raise Exception(error_msg)

    def save_result(self, item_id, result_payload):
        """寫回結算結果（範例以假資料模擬 Cassandra UPDATE）。"""
        try:
            updated_at = UnixNow()
            if self.session:
                # self.session.execute("UPDATE ... SET ... WHERE item_id = %s", (...))
                pass
            return {"item_id": item_id, "updated_at": updated_at, **result_payload}
        except Exception as error:
            error_msg = f"save_result failed: item_id={item_id}, error={error}"
            self.send_msg(error_msg, level="Error")
            raise Exception(error_msg)
