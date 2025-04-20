# app/scheduler.py

from pytz import timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.jobs.daily_scrape import run_daily_batch
from app.database import get_db_connection, get_last_mc_scraped

def start_scheduler() -> None:
    scheduler = AsyncIOScheduler(timezone=timezone("Asia/Karachi"))

    # 1) figure out where we start and where we need to stop
    with get_db_connection() as conn, conn.cursor() as cur:
        starting_mc = get_last_mc_scraped(cur)
    target_mc = starting_mc + 500

    def _daily_job():
        # run your batch (which will attempt up to 500 inserts)
        run_daily_batch()

        # check how far we've gotten
        with get_db_connection() as conn, conn.cursor() as cur:
            current_mc = get_last_mc_scraped(cur)

        # if we've hit our 500‑record goal, tear down the scheduler
        if current_mc >= target_mc:
            scheduler.remove_job("daily_fmcsa_batch")
            scheduler.shutdown()

    # 2) schedule it once a day at 15:30 New_York time
    scheduler.add_job(
        _daily_job,
        trigger="cron",
        hour=15,
        minute=35,
        id="daily_fmcsa_batch",
        misfire_grace_time=60 * 60,   # 1 hour
    )

    scheduler.start()
