import sys
import pathlib
import posixpath
import asyncio
import traceback
import time
from datetime import datetime
from queue import Empty, Full, Queue
from threading import Event, Thread
from types import SimpleNamespace
import AppSettings
from Tasks import Tasks
from TCZB import LogLevel, Logger, Versioning
from AppSettings import service_config
from Provider.example import ExampleProvider
from Service.example import ExampleService

logger = None
environment = ""
log_queue = Queue(maxsize=5000)  # log 全部進 queue，避免同步 PostLog 卡住 event loop
log_worker_stop_event = Event()


def send_msg(msg="", level="Error"):
    """傳送訊息至 gateway，參數為 Local 時印出所有訊息但不傳送。
        打印顏色的設置 [白:正常訊息], [紅:有問題,要查看,不可持續出現], [藍:其他打印,要查看,沒問題就無視]

    Args:
        msg (str): 預設空字串，報錯時可自行加入查看的訊息
        level (str): 預設 Error；其餘為 Information, Warning, Critical, Trace, Debug
    """
    color = {
        "Information": "97",  # 白
        "Error": "91",        # 紅
        "Warning": "91",      # 紅
        "Critical": "94",     # 藍
        "Trace": "94",        # 藍
        "Debug": "94",        # 藍
    }
    sys_log = traceback.format_exc()
    send_message = msg if sys_log == "NoneType: None\n" else f"{msg}\n{sys_log}"
    if environment == "Local":
        print(f"\033[{color.get(level, '97')}m開發測試:{level} {send_message}\033[0m")
    try:
        log_queue.put_nowait((send_message, level))
    except Full:
        return


def send_msg_by_queue():
    global logger
    # 所有 level 都在這裡統一送出，避免 event loop 被同步 Kafka I/O 阻塞
    while not log_worker_stop_event.is_set() or not log_queue.empty():
        try:
            send_message, log_level = log_queue.get(timeout=0.5)
        except Empty:
            continue
        try:
            level_name = getattr(LogLevel.LogLevel, log_level, LogLevel.LogLevel.Error).name
            logger.PostLog(level_name, str(send_message))
        except Exception:
            print("send_msg_by_queue 發生錯誤", flush=True)


def init_logger(target_environment):
    """
    初始化 logger，解析環境名稱並計算版本時間。

    Args:
        target_environment (str): 環境名稱，例如 Local、PRD

    Returns:
        str: 版本時間字串（YYYY-MM-DD HH:MM）
    """
    global environment, logger
    environment = target_environment
    project_path = AppSettings.environment_path[environment]
    logger = Logger.Logger(AppSettings.project_name, project_path["logger_config"])
    base_path = pathlib.Path(__file__).parent.absolute()
    versions = [
        str(Versioning.LastModifiedTime(base_path))[:16],
        str(Versioning.LastModifiedTime(posixpath.join(base_path, "Service")))[:16],
        str(Versioning.LastModifiedTime(posixpath.join(base_path, "Provider")))[:16],
    ]
    version = max(versions, key=lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M"))
    send_msg(f"{AppSettings.project_name} starts, version: {version}, environment: {environment}", level="Information")
    return version


async def run(version: str) -> None:
    """
    服務主流程：建立 provider、組裝 service，啟動背景任務後持續執行。

    Args:
        version (str): 版本字串
    """
    stop_event = asyncio.Event()
    provider = SimpleNamespace(
        example=ExampleProvider(send_msg),
    )
    tasks_service = Tasks(send_msg, service_config, version)
    await tasks_service.run()
    example_service = ExampleService(send_msg, provider)
    try:
        while not stop_event.is_set():
            processed = await example_service.process(source="default")
            send_msg(f"processed {processed} records", level="Information")
            await asyncio.sleep(service_config.get("poll_interval_seconds", 30))
    finally:
        stop_event.set()
        await tasks_service.stop()


def main() -> None:
    target_environment = sys.argv[1]
    version = init_logger(target_environment)
    log_worker_stop_event.clear()
    log_worker = Thread(target=send_msg_by_queue, daemon=True)
    log_worker.start()
    try:
        asyncio.run(run(version))
    except Exception:
        send_msg("service crashed with unexpected exception", level="Error")
        time.sleep(3)


if __name__ == "__main__":
    main()

"""
python .\project\__main__.py Local
"""
