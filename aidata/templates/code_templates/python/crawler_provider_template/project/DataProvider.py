import requests
import os
import time
from functools import wraps
import threading

class DataProvider(object):
    def __init__(self, send_msg):
        self.send_msg = send_msg
        self.session = None
        self.error_count = 0
        self.requests_count = 0
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.3",
        }

    def rate_limiter(max_calls: int, period: float, avg_mode: bool = False, show_log: bool = False):
        """
        用於限制請求頻率

        Args:
            max_calls (int): 每個週期允許的最大呼叫次數
            period (float): 週期長度（秒）
            avg_mode (bool): True 則使用平均等待模式（每次呼叫間隔固定為 period/max_calls）
            show_log: 顯示請求等待的log

        Returns:
            decorator (function): 回傳實際作用於目標方法的裝飾器
        """
        lock = threading.Lock()
        waiting_lock = threading.Lock()
        waiting_count = 0  # 記錄有多少請求正在等待
        # --- avg_mode=True 會用到 ---
        next_allowed_time = 0.0
        interval = period / max_calls
        # --- avg_mode=False 會用到 ---
        call_times = []

        def decorator(func):
            @wraps(func)
            def wrapper(self, *args, **kwargs):
                nonlocal next_allowed_time, call_times, waiting_count
                if avg_mode:
                    while True:
                        with lock:
                            now = time.monotonic()
                            sleep_time = max(0.0, next_allowed_time - now)
                            base = max(now, next_allowed_time)
                            next_allowed_time = base + interval

                        if sleep_time > 0:
                            with waiting_lock:
                                waiting_count += 1
                                if show_log: print(f"[{time.strftime('%H:%M:%S')}] 有 {waiting_count} 個請求正在等待 (avg_mode)，預計睡 {sleep_time:.3f}s")
                            time.sleep(sleep_time)
                            with waiting_lock:
                                waiting_count -= 1
                            break
                        else:
                            break
                else:
                    while True:
                        with lock:
                            now = time.monotonic()
                            # 滑動視窗內的呼叫紀錄
                            call_times = [t for t in call_times if now - t < period]

                            if len(call_times) >= max_calls:
                                oldest = call_times[0]
                                sleep_time = period - (now - oldest)
                            else:
                                call_times.append(now)
                                sleep_time = 0.0
                        if sleep_time > 0:
                            with waiting_lock:
                                waiting_count += 1
                                if show_log: print(f"[{time.strftime('%H:%M:%S')}] 有 {waiting_count} 個請求正在等待 (burst_mode)，預計睡 {sleep_time:.3f}s")
                            time.sleep(sleep_time)
                            with waiting_lock:
                                waiting_count -= 1
                            continue
                        else:
                            break
                return func(self, *args, **kwargs)
            return wrapper
        return decorator

    @rate_limiter(max_calls=8, period=1, avg_mode=False) #網站比較會擋的話就自己改限流參數
    def requests_data(self, url, method="get", format="text", post_data=[]):
        try:
            resp_data = ""
            status_code = ""
            session = self.get_session()
            self.requests_count += 1
            if method == "get":
                if post_data:
                    respone = session.get(url, timeout = 60, params=post_data, headers=self.headers)
                else:
                    respone = session.get(url, timeout = 60, headers=self.headers)
            else:
                if post_data:
                    respone = session.post(url, json=post_data, timeout = 5, headers=self.headers)
                else:
                    respone = session.post(url, timeout = 60, headers=self.headers)
            status_code = respone.status_code
            resp_data = eval(f"respone.{format}")
            if status_code in [200, 204]:
                self.error_count = 0
            else:
                raise
            return resp_data
        except:
            self.error_count += 1
            if self.error_count >= 30:
                os._exit(0)
            msg = f"url: {url}, method: {method} , format: {format}, post_data: {post_data}, status_code: {status_code}, error_count:{self.error_count}"
            self.send_msg(msg=msg, level="Warning")
            return "" if format == "text" else {}


    def get_session(self):
        if self.session is None:
            self.session = requests.Session()
        return self.session


    def close_session(self):
        if self.session is not None:
            self.session.close()
            self.session = None
