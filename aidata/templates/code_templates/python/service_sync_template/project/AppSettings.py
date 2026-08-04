project_name = "XXXXService"
Local_logger_config = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
PRD_logger_config = ["49.213.1.158:29096"] #外網 部在.9.10.11用這個
environment_path = {
    "Local":{ #開發用 不展示畫面
        "logger_config":  Local_logger_config,
    },
    "PRD":{
        "logger_config":  PRD_logger_config,
    },
}


service_config = {
}
