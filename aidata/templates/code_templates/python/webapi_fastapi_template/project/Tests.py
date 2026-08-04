import unittest
from typing import Any, Callable
from fastapi import FastAPI
from fastapi.testclient import TestClient
from Resources.example import ExampleRoutes


class BaseApiTestCase(unittest.TestCase):
    client: TestClient = None

    @classmethod
    def set_client(cls, client: TestClient):
        cls.client = client


class ExampleTests(BaseApiTestCase):
    def test_get_items(self):
        response = self.client.get("/api/example/books?limit=5")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_items_with_keyword(self):
        response = self.client.get("/api/example/books?keyword=A&is_active=true&limit=5")
        self.assertEqual(response.status_code, 200)

    def test_get_items_with_start_date(self):
        response = self.client.get("/api/example/books?start_date=2026-03-01&sort_by=priority")
        self.assertEqual(response.status_code, 200)

    def test_get_items_invalid_date_format(self):
        response = self.client.get("/api/example/books?start_date=20260301")
        self.assertEqual(response.status_code, 422)

    def test_get_items_limit_too_large(self):
        response = self.client.get("/api/example/books?limit=999")
        self.assertEqual(response.status_code, 422)

    def test_create_item(self):
        response = self.client.post("/api/example/books", json={
            "name": "測試項目",
            "description": "這是描述",
            "tags": ["新品", "推薦"],
            "priority": 5,
            "is_public": True,
        })
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("id", data)
        self.assertIn("tags", data)
        self.assertIn("is_public", data)

    def test_create_item_minimal(self):
        response = self.client.post("/api/example/movies", json={"name": "最小參數項目"})
        self.assertEqual(response.status_code, 200)

    def test_create_item_priority_out_of_range(self):
        response = self.client.post("/api/example/books", json={"name": "超出範圍", "priority": 99})
        self.assertEqual(response.status_code, 422)

    def test_create_item_missing_name(self):
        response = self.client.post("/api/example/books", json={"description": "缺少 name"})
        self.assertEqual(response.status_code, 422)


def create_test_app(provider=None, send_msg=None) -> FastAPI:
    """
    建立測試用 FastAPI 實例，路由與正式 create_app 對齊。

    Args:
        provider (Any | None): 測試用 provider（可為 None）
        send_msg (Callable | None): log 回呼（可為 None）

    Returns:
        FastAPI: 測試用 app 實例
    """
    app = FastAPI()
    app.state.provider = provider
    app.state.send_msg = send_msg
    app.include_router(ExampleRoutes.router)
    return app


def run_tests(provider: Any | None = None, send_msg: Callable[..., Any] | None = None, *, environment_name: str | None = None):
    """
    執行 API unittest 套件。

    Args:
        provider (Any | None): 測試用 app 的 provider（可為 None）。
        send_msg (Callable[..., Any] | None): log 回呼（可為 None）。
        environment_name (str | None): 環境名稱，例如 Local、PRD。
    """
    app = create_test_app(provider=provider, send_msg=send_msg)
    with TestClient(app, raise_server_exceptions=False) as client:
        test_classes = [
            ExampleTests,
        ]
        suite = unittest.TestSuite()
        loader = unittest.TestLoader()
        for test_class in test_classes:
            if hasattr(test_class, "set_client"):
                test_class.set_client(client)
            suite.addTests(loader.loadTestsFromTestCase(test_class))
        result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError("Tests failed, service startup aborted.")
