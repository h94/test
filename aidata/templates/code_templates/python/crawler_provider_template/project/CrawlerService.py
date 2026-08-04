from TCZB import Globals, Datetime
from datetime import datetime
import time
import json
import os
import threading
import gzip
import base64
import random
import re

class CrawlerService(object):
    def __init__(self, service_inputs):
        self.kafka_producers = service_inputs["kafka_producers"]
        self.machine_name = service_inputs["machine_name"]
        self.environment = service_inputs["environment"]
        self.version = service_inputs["version"]
        self.send_msg = service_inputs["send_msg"]
        self.provider = service_inputs["provider"]
        self.open_web = service_inputs["open_web"]
        self.heart_txt = service_inputs["heart_txt"]
        self.topic = service_inputs["topic"]
        self.setting = Globals.Globals.CrawlerData["service"]
        self.driver = None #有使用selenium的話，用self.driver存driver物件
        self.start_time = time.time()
        threading.Thread(target=self.listen_status, daemon=True).start()
        threading.Thread(target=self.call_dashboard, daemon=True).start()
        threading.Thread(target=self.check_running_6H, daemon=True).start()


    def main(self):
        self.start_time = time.time()
        print("123")
        time.sleep(1)

    def send_data(self, game_type, page_type, data):
        """送出資料到Game Data

        Args:
            game_type: "SC" "BK"
            page_type: "pregame" "inplay" "result"
            data: 比賽資料
        """
        try:
            result = {
                "game_type": game_type,
                "page_type": page_type,
                "machine_name": self.machine_name,
                "timestamp": Datetime.UnixNow(),
                "data": data,
            }
            for kafka in self.kafka_producers:
                kafka.Send(self.topic, json.dumps(result))
        except:
            self.send_msg(msg=f"gametype:{game_type} pagetype:{page_type}")

    def close_program(self):
        """
        有用selenium時，用這個function關閉爬蟲，沒用的話刪掉
        1.關閉driver 2.kill 工作管理員的driver(通常1就能正常關閉)
        """
        try:
            if self.driver:
                self.driver.quit()
        except:
            self.send_msg()
        try:
            tasklist = os.popen('tasklist').read()
            if "XXXXdriver.exe" in tasklist:
                os.system("taskkill /f /im XXXXdriver.exe") #保險用  若quit()失敗時 由kill強制關閉
        except:
            self.send_msg()

        os._exit(0)


    def listen_status(self):
        while True:
            try:
                with open(self.heart_txt, 'r') as f:
                    status = f.read()
                if status == "0":
                    msg = "Control close program."
                    self.send_msg(msg=msg, level="Information")
                    self.close_program()
                time.sleep(5)
            except:
                self.send_msg()
                time.sleep(5)
                continue


    def check_running_6H(self):
        while True:
            now = time.time()
            if self.start_time != "":
                if (now-self.start_time) > 21600:
                    msg = "Running 6H, close program."
                    self.send_msg(msg=msg, level="Information")
                    self.close_program()
            time.sleep(5)


    def call_dashboard(self):
        need_send = random.randint(1,9)
        while True:
            try:
                time.sleep(10)
                dashboard_msg = "test"
                dashboard_path = {"machine_name":self.machine_name, "page": dashboard_msg, "version": self.version}
                if self.version != "test": #開發時不call dashboard(或者上線的爬蟲，爬蟲沒有預計在開發機上運行)
                    dashboard_url = self.setting["price_center_api"]["dashboard"].format(**dashboard_path)
                    self.provider.requests_data(dashboard_url, method="post")
                need_send += 1
                if need_send >= 10:
                    msg = f"{datetime.now()} program alive, version is {self.version}, requests count: {self.provider.requests_count}, dashboard_msg: {dashboard_msg}"
                    self.send_msg(msg=msg, level="Information")
                    need_send = 0
                self.provider.requests_count = 0
            except:
                self.send_msg()
            time.sleep(50)