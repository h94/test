from TCZB import Logger, LogLevel, Globals, Versioning
import AppSettings
import socket
import traceback
import pathlib
import sys
from Provider.example import ExampleProvider
from Tasks import Tasks
from types import SimpleNamespace

def send_msg(msg = "", level = "Error", ):
    """ 傳送訊息至getway, 參數為Local時,印出所有訊息但不傳送
        如果只是要單純傳送訊息而非報錯,sys_log會回報"NoneType: None\n",則不會加入訊息內
        打印顏色的設置 [白:正常訊息], [紅:有問題,要查看,不可持續出現], [藍:其他打印,要查看,沒問題就無視]
    Args:
        level (str): 預設Error,報錯是最常用的其餘為Information,Warning,Critical,Trace,Debug
        msg (str): 預設空字串,報錯時可自行加入查看的訊息
    """
    color = {
        "Information":"97", #白
        "Error": "91", #紅
        "Warning": "91", #紅
        "Critical": "94", #藍
        "Trace": "94", #藍
        "Debug": "94", #藍
    }
    sys_log = traceback.format_exc()
    send_message = msg if sys_log == "NoneType: None\n" else f"{msg}\n{sys_log}"
    if environment == "Local" or True:
        print(f"\033[{color[level]}m開發測試:{level} {send_message}\033[0m")
    send_message = f"env:{environment}" + "\n\n" + str(send_message)
    logger.PostLog(eval(f"LogLevel.LogLevel.{level}.name"), send_message)



def create_provider_object():
    """
    建立provider object
    """
    return SimpleNamespace(
        example=ExampleProvider(send_msg),
    )


def main():
    try:
        global environment, logger
        environment = sys.argv[1]
        environment_path = AppSettings.environment_path
        if environment not in environment_path : return
        project_path = environment_path[environment]
        Globals.Globals.CrawlerData = AppSettings.service_config
        project_name = AppSettings.project_name
        version = str(Versioning.LastModifiedTime(pathlib.Path(__file__).parent.absolute()))[:16]
        logger = Logger.Logger(AppSettings.project_name, project_path["logger_config"])
        logger.PostLog(LogLevel.LogLevel.Information.name, f"{project_name} starts, version: {version}, environment: {environment}")
        provider = create_provider_object()
        service_inputs = {
            "machine_name": socket.gethostname(),
            "environment": environment,
            "setting": AppSettings.service_config,
            "version": version,
            "provider":provider,
            "send_msg": send_msg,
        }
        tasks_service = Tasks(service_inputs)
        tasks_service.run()
    except:
        error_msg = f"{traceback.format_exc()}"
        print(error_msg)
        return

if __name__ == "__main__":
    main()