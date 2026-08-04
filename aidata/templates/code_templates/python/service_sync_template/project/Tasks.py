import time
import threading

class Tasks:
    def __init__(self,service_inputs) -> None:
        self.send_msg = service_inputs["send_msg"]
        self.setting = service_inputs["setting"]
        self.send_msg = service_inputs["send_msg"]
        self.version = service_inputs["version"]

    def run(self):
        """
        如果定義了需要執行的任務，則在這裡開啟thread
        """
        threading.Thread(target=self.call_gateway, daemon=True).start()



    def call_gateway(self):
        """
        heartbeat
        """
        while True:
            try:
                message = f"version:{self.version} prgram alive"
                self.send_msg(message, level="Information")
            except:
                self.send_msg()
            time.sleep(600)