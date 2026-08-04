import asyncio

class Tasks:
    def __init__(self, send_msg, app, settings) -> None:
        self.send_msg = send_msg
        self.app = app
        self.setting = settings
        self.background_tasks = []

    def run(self):
        """
        如果定義了需要執行的任務，則在這裡開啟背景 task
        """
        self.background_tasks.append(asyncio.create_task(self.call_gateway()))

    async def stop(self):
        if not self.background_tasks: return
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()

    async def call_gateway(self):
        while True:
            try:
                message = f"version:{self.app.state.version} request count:{self.app.state.request_count}"
                self.send_msg(message, level="Information")
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.send_msg(f"heartbeat 異常: {error}", level="Error")
            self.app.state.request_count = 0
            await asyncio.sleep(60)

