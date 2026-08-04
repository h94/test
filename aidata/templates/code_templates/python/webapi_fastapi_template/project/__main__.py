import pathlib
import posixpath
import socket
import sys
import time
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from queue import Empty, Full, Queue
from threading import Event, Thread
from types import SimpleNamespace
import AppSettings
import uvicorn
from TCZB import LogLevel, Logger, Versioning
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from Tasks import Tasks
from Tests import run_tests
from Provider.example import ExampleProvider
from Resources.example import ExampleRoutes

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
    # 所有 level 都在這裡統一送出，避免 request thread/event loop 被同步 Kafka I/O 阻塞
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
    初始化 logger 並記錄版本與環境資訊。

    Args:
        target_environment (str): 環境名稱，例如 Local、PRD

    Returns:
        tuple: (project_path dict, version str)
    """
    global environment, logger
    environment = target_environment
    environment_path = AppSettings.environment_path
    project_path = environment_path[environment]
    logger = Logger.Logger(AppSettings.project_name, project_path["logger_config"])
    base_path = pathlib.Path(__file__).parent.absolute()
    versions = [
        str(Versioning.LastModifiedTime(base_path))[:16],
        str(Versioning.LastModifiedTime(posixpath.join(base_path, "Resources")))[:16],
        str(Versioning.LastModifiedTime(posixpath.join(base_path, "Service")))[:16],
        str(Versioning.LastModifiedTime(posixpath.join(base_path, "Provider")))[:16],
    ]
    version = max(versions, key=lambda value: datetime.strptime(value, "%Y-%m-%d %H:%M"))
    send_msg(f"{AppSettings.project_name} starts, version: {version}, environment: {environment}", level="Information")
    return project_path, version


def create_app(version):
    """
    建立並設定 FastAPI app，注入 provider 與 app.state。

    Args:
        version (str): 版本字串

    Returns:
        FastAPI: 已設定完成的 app 實例
    """
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        tasks_service = None
        log_worker_stop_event.clear()
        log_worker = Thread(target=send_msg_by_queue, daemon=True)
        log_worker.start()
        try:
            provider = SimpleNamespace(
                example=ExampleProvider(send_msg),
            )
            app.state.provider = provider
            app.state.request_count = 0
            app.state.version = version
            app.state.environment = environment
            app.state.send_msg = send_msg
            tasks_service = Tasks(send_msg, app, AppSettings.service_config)
            app.state.tasks = tasks_service
            tasks_service.run()
            yield
        finally:
            if tasks_service is not None:
                await tasks_service.stop()
            log_worker_stop_event.set()
            log_worker.join(timeout=2)

    app = FastAPI(
        title=AppSettings.project_name,
        version=f"v{version}",
        openapi_url="/openapi.json",
        docs_url="/swagger-ui",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def request_count_middleware(request: Request, call_next):
        request.app.state.request_count = getattr(request.app.state, "request_count", 0) + 1
        return await call_next(request)

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        detail = exc.detail
        if not isinstance(detail, str):
            detail = str(detail)
        detail = detail.replace("\n", " ").replace("\r", " ")[:500]
        return JSONResponse(status_code=exc.status_code, content={"detail": detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        send_msg(f"unhandled API error {request.method} {request.url.path}: {exc}", level="Error")
        detail = str(exc).replace("\n", " ").replace("\r", " ")[:500] or "internal server error"
        return JSONResponse(status_code=500, content={"detail": detail})

    app.include_router(ExampleRoutes.router)
    return app


def main():
    try:
        target_environment = sys.argv[1]
        skip_tests = len(sys.argv) > 2 and sys.argv[2] == "NoTest"
        project_path, version = init_logger(target_environment)
        app = create_app(version)
        if skip_tests:
            print("略過啟動前測試（NoTest）", flush=True)
        else:
            run_tests(send_msg=send_msg, environment_name=environment)
        machine_name = socket.gethostname()
        host = "127.0.0.1" if machine_name.startswith("DESKTOP") else "0.0.0.0"
        uvicorn.run(app, host=host, port=5000)
    except Exception:
        send_msg("service initialization failed", level="Error")
        time.sleep(3)


if __name__ == "__main__":
    main()

"""
python .\project\__main__.py Local
python .\project\__main__.py Local NoTest   # 略過啟動前測試，直接啟動服務
"""
