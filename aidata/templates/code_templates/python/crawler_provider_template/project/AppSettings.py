"""
kafka_9, 10, 11 存放任何種類的*HTML*, 只要是接收或傳送HTML都是依照機器打至對應的KAFKA
kafka_9, HK, BAK 存放 *game_data*, parser解析完的資料依照機器打至對應的KAFKA
provider:只會送KAFKA到kafka_9, 10, 11
parser:會從kafka_9, 10, 11接收資料,再送到kafka_9, HK, BAK
"""

site = 'XXXX'
project_name = f"XXXXProvider"
# topic = f"{site}html"
topic = "test"
heart = f'C:\Heart\heartXXXX.txt'
Local_logger_config = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
PRD_logger_config = ["49.213.1.158:29096"]
kafka_9 = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
kafka_10 = ["192.168.10.231:9092", "192.168.10.232:9092", "192.168.10.233:9092"]
kafka_11 = ["192.168.11.231:9092", "192.168.11.232:9092"]
environment_path = {
    "Local":{
        "logger_config":  Local_logger_config,
        "send_html_data": [kafka_9]  #**provider** 送 html      **main的kafka_producers要設好對的key**
    },
    "PRD":{
        "logger_config":  PRD_logger_config,
        "send_html_data": [kafka_9]
    },
    "PRD2":{
        "logger_config":  PRD_logger_config,
        "send_html_data": [kafka_10]
    },
    "PRD3":{
        "logger_config":  PRD_logger_config,
        "send_html_data": [kafka_11]
    },
}

settings = {
    "service":{
        "home_page": "https://站台首頁網址",
        "price_center_api":{
            "dashboard":"https://ls2.zbdigital.net/backend/api/system/machines/{machine_name}/XXXX?status=P:{page},V:{version},H:", #post不帶東西
        },
        "game_type":{ #需要抓的球種，特定球種不想抓可以直接註解

        },
    },
    "transformer":{},
}
