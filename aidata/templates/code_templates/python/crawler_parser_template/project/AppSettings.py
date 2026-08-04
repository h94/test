"""
kafka_9, 10, 11 存放任何種類的*HTML*, 只要是接收或傳送HTML都是依照機器打至對應的KAFKA
kafka_9, HK, BAK 存放 *game_data*, parser解析完的資料依照機器打至對應的KAFKA
provider:只會送KAFKA到kafka_9, 10, 11
parser:會從kafka_9, 10, 11接收資料,再送到kafka_9, HK, BAK
"""

project_name = "CrawlerAgentXxxx"
source = "xxxx.com"
site_type = "score" # score 或 odd,  沒有賠率的比分站台用score, 有賠率的用odd
topic = "xxxxhtml"
group_ID = "zbxx"
gamedata_path = "gamedata2" #修改舊站台時 原本用什麼就改什麼 新站台都用2
Local_logger_config = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
PRD_logger_config = ["49.213.1.158:29096"] #外網 部在.9.10.11用這個
PROD_logger_config = ["192.168.55.60:9092"] #內網 部在8X6X用這個
kafka_9 = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
kafka_10 = ["192.168.10.231:9092", "192.168.10.232:9092", "192.168.10.233:9092"]
kafka_11 = ["192.168.11.231:9092", "192.168.11.232:9092"]
kafka_HK = ["49.213.1.158:29097", "49.213.1.158:29098", "49.213.1.158:29099"]
kafka_BAK = ['49.213.1.156:29095']
environment_path = {
    "Show":{ #開發用 可展示畫面
        "logger_config":  Local_logger_config,
        "receive_kafka":  kafka_9,
        "send_game_data": [kafka_9], #**parser** 送 game_data   **main的kafka_producers要設好對的key**
        "send_html_data": [kafka_9]  #**provider** 送 html      **main的kafka_producers要設好對的key**
    },
    "Local":{ #開發用 不展示畫面
        "logger_config":  Local_logger_config,
        "receive_kafka":  kafka_9,
        "send_game_data": [kafka_9],
        "send_html_data": [kafka_9]
    },
    "PRD":{
        "logger_config":  PRD_logger_config,
        "receive_kafka":  kafka_9,
        "send_game_data": [kafka_9, kafka_HK, kafka_BAK],
        "send_html_data": [kafka_9]
    },
    "PRD2":{
        "logger_config":  PRD_logger_config,
        "receive_kafka":  kafka_10,
        "send_game_data": [kafka_HK, kafka_BAK],
        "send_html_data": [kafka_10]
    },
    "PRD3":{
        "logger_config":  PRD_logger_config,
        "receive_kafka":  kafka_11,
        "send_game_data": [kafka_HK, kafka_BAK],
        "send_html_data": [kafka_11]
    },
    "PROD":{
        "logger_config":  PROD_logger_config,
        "receive_kafka":  kafka_11,
        "send_game_data": [kafka_HK, kafka_BAK],
        "send_html_data": [kafka_11]
    },
}
InProgress = "0"
Final = "1"
Scheduled = "2"
Postponed = "3"
Cancelled = "4"
gamedata_update_path = {
    "gamedata": 2,
    "other": 4,
}
settings = {
    "namemap_url":"https://ls.zbdigital.net/api/site/namemap",
    "service": {
        "gamedata_update_speed": gamedata_update_path.get(gamedata_path, gamedata_update_path["other"])
    },
    "provider":{},
    "transformer":{},
}
