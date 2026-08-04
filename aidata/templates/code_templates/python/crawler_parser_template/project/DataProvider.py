from TCZB import Kafka, Datetime
import json
import requests
import time
import queue

class DataProvider(object):
    def __init__(self, logger, topic, receive_kafka, group_ID, send_msg):
        self.logger = logger
        self.generator = None
        self.session = None
        self.send_msg = send_msg
        self.latest_send_time = time.time()
        self.save_lang = queue.Queue()
        self.setup_kafka_consumer(topic, receive_kafka, group_ID)


    def setup_kafka_consumer(self, topic, bootstrapServers, groupID = None, autoOffsetReset = "latest", autoCommit = True, autoCommitInterval = 5000):
        """Create and a generator that retrieves kafka messages and assign it to self.generator
        Args:
            topic (str): Kafka topic
            bootstrapServers (List[str]): Each string contains ip and port ("IP:Port")
            groupID (str, optional): Kafka's group id. Defaults to None.
            autoOffsetReset (str, optional): Options: "earliest","latest". Starting point of when kafka group is new. Defaults to 'latest'.
            autoCommit (bool, optional): Tells kafka that the message is consumed. Defaults to True.
            autoCommitInterval (int, optional): Intervel between auto commits(in ms). Defaults to 5000.
        """
        try:
            kafkaConsumer = Kafka.Kafka(self.logger)
            self.generator = kafkaConsumer.MessageGenerator(topic, bootstrapServers, groupID, autoOffsetReset, autoCommit, autoCommitInterval)
        except:
            self.send_msg()


    def get_kafka(self):
        """Continuously send match data
        Raises:
            # StopIteration: self.kafkaConsumer is not initialized
        Yields:
            Iterator[Tuple[str, str, int, str, lxml.etree._Element]]: Generator that continues to yield a tuple of
                                            patge type, game type, request time, source machine name, and xml data
        """
        try:
            if self.generator:
                for message in self.generator:
                    if not self.check_kafka_time(message): continue
                    message = message.value.decode("UTF8")
                    yield self.read_data(message)
        except:
            self.send_msg()


    def check_kafka_time(self, message):
        """判別kafka自帶的時間戳是否與現時差距是否小於5秒
           message.timestamp為13碼的時間戳(1660028996604)
           time.time()*1000也為13碼+小數點的時間戳(1660198656461.1294) 小數點後可無視
           兩者相減/1000則為差距秒數
        Args:
            message (boject): kafka的物件

        Returns:
            bool: True or False
        """
        try:
            return (time.time()*1000-message.timestamp)/1000 < 5
        except:
            self.send_msg()


    def read_file(self):
        try:
            path = r"D:\GameData\yourfile.txt"
            with open(path, "r", encoding="utf-8") as f:
                for message in f.readlines():
                    yield self.read_data(message)
        except:
            self.send_msg()


    def read_data(self, message):
        try:
            success, request_time, provider_name, time_stamp, lang, game_type, page_type, game_html =  (None,) * 8
            request_time = Datetime.UnixNow()
            #---------------------------------------------
            #success固定寫在最上跟最下
            #以下依照情況處理成自己需要的
            json_data = json.loads(message)
            game_type = json_data["game_type"]
            provider_name = json_data["provider_name"]
            time_stamp = json_data["time_stamp"]
            lang = json_data["lang"]
            page_type = json_data["page_type"]
            game_html = json_data["game_html"]

            #--------------------------------------------
            success = True
        except:
            msg = str(message)[:150]
            self.send_msg(msg=msg)
        return success, request_time, provider_name, time_stamp, lang, game_type, page_type, game_html


    def requests_data(self, url, method="get", process="text", headers={}, post_data=[]):
        """
        method: ["get", "post"]
        process: ["text", "json()"]
        """
        try:
            status_code = 0
            session = self.get_session()
            if method == "get":
                respone = session.get(url, headers=headers, timeout = 10)
            else:
                respone = session.post(url, json=post_data, headers=headers, timeout = 10)
            status_code = respone.status_code
            if status_code == 200:
                return eval(f"respone.{process}")
            else:
                raise
        except:
            self.close_session()
            msg = f"url: {url}, status_code: {status_code}, post_data: {post_data}, method: {method} , process: {process}, headers: {headers}"
            self.send_msg(msg=msg, level="Warning")
            return ""


    def get_session(self):
        try:
            if self.session is None:
                self.session = requests.Session()
            return self.session
        except:
            self.send_msg()


    def close_session(self):
        try:
            if self.session is not None:
                self.session.close()
                self.session = None
        except:
            self.send_msg()


    def test(self):
        """自行測試用  開發請刪掉
        """
        game_datas = [
            json.dumps({"game_type":"ES","page_type":"pregame_list","time_stamp":1735174971242,"lang":"","provider_name":"DESKTOP-ZB06","game_html":[{'league_id':'l1','league':'l1','team_home_id':'th1','team_home':'th1','team_away_id':"ta1",'team_away':"ta1",'game_date':'2025-02-04','game_time':'09:30','game_id':'gid1','score_home':'0','score_away':'0','scores':[],'game_status':'2','double_header':'N','playbyplay':'','odds':{}}]}),
            json.dumps({"game_type":"ES","page_type":"pregame_list","time_stamp":1735174971242,"lang":"","provider_name":"DESKTOP-ZB06","game_html":[{'league_id':'l1','league':'l1','team_home_id':'th1','team_home':'th1','team_away_id':"ta1",'team_away':"ta1",'game_date':'2025-02-04','game_time':'09:30','game_id':'gid1','score_home':'-1','score_away':'-1','scores':[],'game_status':'4','double_header':'N','playbyplay':'','odds':{}}]}),
        ]
        for game_data in game_datas:
            yield self.read_data(game_data)
            time.sleep(0.1)
