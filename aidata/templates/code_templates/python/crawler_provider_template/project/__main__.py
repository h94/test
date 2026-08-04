import CrawlerService
import AppSettings
from TCZB import Logger, LogLevel, Globals, Kafka
import socket
import traceback
import MachinePath
import os
import time
import OpenWeb
import DataProvider


def send_msg(msg = "", level = "Error"):
    """ 傳送訊息至getway, 參數為Local時,印出所有訊息但不傳送
        如果只是要單純傳送訊息而非報錯,sys_log會回報"NoneType: None\n",則不會加入訊息內

    Args:
        level (str): 預設Error,報錯是最常用的其餘為Information,Warning,Critical,Trace,Debug
        msg (str): 預設空字串,報錯時可自行加入查看的訊息
    """
    sys_log = traceback.format_exc()
    send_message = msg if sys_log == "NoneType: None\n" else f"{msg}\n{sys_log}"
    if environment == "Local" or True:
        print("開發測試", send_message)
    logger.PostLog(eval(f"LogLevel.LogLevel.{level}.name"), send_message)
    return sys_log


def main():
    try:
        global environment, logger
        machine_name = socket.gethostname()
        environment = MachinePath.machine_path[machine_name]
        environment_path = AppSettings.environment_path
        if environment not in environment_path : return
        project_path = environment_path[environment]
        Globals.Globals.CrawlerData = AppSettings.settings
        project_name = AppSettings.project_name
        project_folder = os.environ["APPDATA"].split("AppData")[0] + "Desktop\\" + project_name
        project_executable = project_folder +  '\\' + project_name + '.exe'
        driver_executable =  project_folder +  '\\' + project_name.replace("Provider", "driver") + '.exe'
        version = "test"
        if os.path.isfile(project_executable):
            version = time.strftime("%m/%d %H:%M", time.localtime(os.path.getmtime(project_executable)))
        logger = Logger.Logger(AppSettings.project_name, project_path["logger_config"])
        logger.PostLog(LogLevel.LogLevel.Information.name, f"{project_name} starts, version: {version}, environment: {environment}")
        open_web = OpenWeb.OpenWeb(send_msg, project_folder, driver_executable, AppSettings.site)
        provider = DataProvider.DataProvider(send_msg)
        with open(AppSettings.heart, 'w') as f:
            f.write("1")
        service_inputs = {
            "kafka_producers": [Kafka.Kafka(logger, True, server) for server in project_path["send_html_data"]], #provider:"send_html_data",  parser: "send_game_data"
            "machine_name": machine_name,
            "environment": environment,
            "version": version,
            "send_msg": send_msg,
            "provider": provider,
            "open_web" :open_web,
            "heart_txt": AppSettings.heart,
            "topic":AppSettings.topic
        }
        CrawlerService.CrawlerService(service_inputs).main()
    except:
        error_msg = f"{traceback.format_exc()}"
        print(error_msg)
        send_msg(error_msg)
        time.sleep(3)

if __name__ == "__main__":
    main()

'''
pip install pyinstaller
打包成exe
pyinstaller -F --name=XXXXXProvider ./project/__main__.py
'''