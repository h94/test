from TCZB import Globals, Datetime, Redis
import queue
import json
import time
from collections import defaultdict
import threading

class CrawlerService(object):
    def __init__(self, service_inputs):
        self.kafka_producers = service_inputs["kafka_producers"]
        self.machine_name = service_inputs["machine_name"]
        self.environment = service_inputs["environment"]
        self.version = service_inputs["version"]
        self.source = service_inputs["source"]
        self.provider = service_inputs["provider"]
        self.transformer = service_inputs["transformer"]
        self.flow_control = service_inputs["flow_control"]
        self.name_map_service = service_inputs["name_map_service"]
        self.gamedata = service_inputs["gamedata_path"]
        self.send_msg = service_inputs["send_msg"]
        self.redis = Redis.Redis("") # 自行帶入站台名稱
        self.parser_status = None
        self.setting = Globals.Globals.CrawlerData["service"]
        self.latest_send_time = time.time()
        self.send_queue = defaultdict(queue.Queue)
        self.game_queue = defaultdict(queue.Queue)
        self.latest_receive_time = defaultdict(time.time)
        self.game_data_queue = queue.Queue() #開發用 由debug展示
        threading.Thread(target=self.heartbeta_log, daemon=True, args=()).start()
        threading.Thread(target=self.listen_status, daemon=True, args=()).start()


    def GetMatches(self):
        #for provider_data in self.provider.get_kafka():
        #for provider_data in self.provider.read_file():
        for provider_data in self.provider.test():
            if self.parser_status == 0: continue
            success, request_time, provider_name, time_stamp, lang, *data = provider_data
            if not success:continue
            try:
                matches = self.transformer.get_match(time_stamp, lang, data)
                #for match in matches: match.check() # 開發期間打開，檢查資料型態
                if not matches: continue
                if lang:
                    self.name_map_service.name_map_service(matches)
                else:
                    is_local = self.environment == "Local"
                    for match in matches:
                        self.game_queue[match.game_type].put(match)
                    for game_type, game_queue in self.game_queue.items():
                        queue_len = game_queue.qsize()
                        if not queue_len: continue
                        time_diff = time.time()-self.latest_receive_time[game_type]
                        if queue_len >= 30 or time_diff >= self.setting["gamedata_update_speed"] or is_local:
                            self.latest_receive_time[game_type] = time.time()
                            sum_matches = self.get_all_match(game_queue)
                            if sum_matches:
                                change_matches = self.flow_control.flow_control(sum_matches)
                                self.post_match(request_time, provider_name, change_matches, time_stamp)
            except:
                self.send_msg()
                continue


    def get_all_match(self, queue):
        matches = []
        while not queue.empty():
            matches.append(queue.get())
        return matches


    def post_match(self, request_time, provider_name, change_matches, time_stamp):
        try:
            for game_type, change_matches in change_matches.items():
                self.send_queue[game_type].put("1")#計算數量用
                if change_matches:
                    matches = []
                    for i in range(0, len(change_matches), 50):# 切成50場1包
                        matches.append(change_matches[i : i + 50]) # 切成50場1包
                    for part_match in matches:
                        result = {
                        "gametype": game_type,
                        "HeartBeat": 0,
                        "source": self.source,
                        "request_time": request_time,
                        "send_time": Datetime.UnixNow(),
                        "crawler_mode": "RealTime",
                        "machine_name": self.machine_name,
                        "provider_name":provider_name,
                        "matches": part_match
                        }
                        if self.environment == "Show": self.game_data_queue.put(result) #開發用
                        # 確認資料沒問題再開啟
                        print(part_match)
                        #[kafka.Send(self.gamedata, json.dumps(result)) for kafka in self.kafka_producers]
        except:
            self.send_msg()

    def listen_status(self):
        while True:
            self.parser_status = self.redis.get_parser_status()
            time.sleep(60)

    def heartbeta_log(self):
        while True:
            now = time.time()
            if now - self.latest_send_time >= 60:
                self.latest_send_time = now
                total_send = dict(sorted({game_type:  len(self.get_all_match(send_queue)) for game_type, send_queue in self.send_queue.items()}.items()))
                msg = f"Version: {self.version}, send {total_send} matches to gamedata in the last minute."
                self.send_msg(msg=msg, level="Information")
            time.sleep(60)