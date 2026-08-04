project_name = "XXXXService"
Local_logger_config = ["192.168.9.231:9092", "192.168.9.232:9092", "192.168.9.233:9092"]
PRD_logger_config = ["49.213.1.158:29096"]
environment_path = {
    "Local":{
        "logger_config":  Local_logger_config,
    },
    "PRD":{
        "logger_config":  PRD_logger_config,
    },
}

service_config = {
    #服務的配置放這裡讓user修改(DB IP的配置放environment_path)
}