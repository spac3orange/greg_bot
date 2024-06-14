import asyncio
import random
from config import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta


class Scheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.scheduler.start()
        print('scheduler started')

    async def schedule_task(self, timing, g_id, func):
        print(self.scheduler.state)
        run_time = datetime.now() + timedelta(seconds=timing)
        self.scheduler.add_job(func, 'date', run_date=run_time, args=(g_id,))
        print(self.scheduler.state)
        logger.info(f"Task {func} scheduled to run at {run_time}")