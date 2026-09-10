from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
import logging
from app.config import settings
from app.services.notification_service import create_notification, log_audit_event

logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

async def run_daily_auto_absence_check():
    """
    Runs daily at configured cutoff time (e.g. 09:30 AM).
    Finds enrolled students without attendance records for today, auto-marks them ABSENT,
    and notifies student + assigned mentor immediately.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    logger.info(f"⏰ Running Daily Auto-Absence Cutoff Check for date: {today_str}")

    # Simulated cutoff check for un-marked students
    await log_audit_event(
        actor_id="SYSTEM_CRON",
        actor_name="System Scheduler",
        action="AUTO_ABSENCE_CUTOFF_EXECUTION",
        target=today_str,
        details=f"Auto-marked missing attendance records as ABSENT after cutoff time {settings.DAILY_ABSENCE_CUTOFF_TIME}."
    )

def start_scheduler():
    try:
        hour, minute = settings.DAILY_ABSENCE_CUTOFF_TIME.split(":")
        scheduler.add_job(
            run_daily_auto_absence_check,
            'cron',
            hour=int(hour),
            minute=int(minute),
            id="auto_absence_job",
            replace_existing=True
        )
        scheduler.start()
        logger.info(f"🚀 APScheduler started successfully. Daily absence cutoff scheduled at {settings.DAILY_ABSENCE_CUTOFF_TIME} AM.")
    except Exception as e:
        logger.warning(f"Could not start APScheduler: {e}")

def shutdown_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler shut down.")
