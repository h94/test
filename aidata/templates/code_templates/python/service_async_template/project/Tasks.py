import asyncio


class Tasks:
    def __init__(self, send_msg, config, version) -> None:
        self.send_msg = send_msg
        self.setting = config
        self.version = version
        self.background_tasks = []

    async def run(self):
        """
        如果定義了需要執行的任務，則在這裡開啟背景 task
        """
        self.background_tasks.append(asyncio.create_task(self.heartbeat()))

    async def stop(self):
        if not self.background_tasks: return
        for task in self.background_tasks:
            task.cancel()
        await asyncio.gather(*self.background_tasks, return_exceptions=True)
        self.background_tasks.clear()

    async def heartbeat(self):
        """週期性回報版本與存活狀態。"""
        while True:
            try:
                self.send_msg(f"version:{self.version} heartbeat", level="Information")
            except asyncio.CancelledError:
                raise
            except Exception as error:
                self.send_msg(f"heartbeat 異常: {error}", level="Error")
            await asyncio.sleep(60)
