class ExampleService:
    """
    範例 Service：業務驗證、結算規則、組裝更新欄位。
    僅透過 __main__.py 注入的 provider（provider.example）存取資料層。
    """

    def __init__(self, send_msg, provider, setting=None) -> None:
        self.send_msg = send_msg
        self.provider = provider
        self.setting = setting or {}

    def validate_item(self, item):
        """業務向參數預檢（應在 Service 完成，不在 Provider）。"""
        if not item or not item.get("item_id"):
            return False, "item_id 不可為空"
        if item.get("status") != "pending":
            return False, f"status 非 pending: {item.get('status')}"
        return True, ""

    def settle_item(self, item):
        """結算單筆項目，回傳待寫回的 payload。"""
        multiplier = self.setting.get("example_payout_multiplier", 2)
        amount = item.get("amount", 0)
        return {"status": "settled", "payout": amount * multiplier}

    def run_once(self, limit=100):
        """一次處理流程：讀取 → 驗證 → 結算 → 寫回。"""
        items = self.provider.example.fetch_pending_items(limit=limit)
        if not items:
            return []

        results = []
        for item in items:
            ok, reason = self.validate_item(item)
            if not ok:
                self.send_msg(f"skip item: {reason}", level="Warning")
                continue
            payload = self.settle_item(item)
            saved = self.provider.example.save_result(item["item_id"], payload)
            results.append(saved)
        return results
