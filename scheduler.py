from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from db import get_users, get_schedule, get_replacement
from utils import get_week_type

scheduler = AsyncIOScheduler()

def start_scheduler(bot):
    scheduler.add_job(send_all, "interval", minutes=1, args=[bot])
    scheduler.start()

async def send_all(bot):
    now = datetime.now().strftime("%H:%M")
    weekday = datetime.now().isoweekday()
    week_type = get_week_type()

    for user_id, time in get_users():
        if time != now:
            continue

        lessons = get_schedule(week_type, weekday)
        if not lessons:
            continue

        text = "📚 Расписание на сегодня:\n"
        for i, subj in lessons:
            text += f"{i}. {subj}\n"

        await bot.send_message(user_id, text)
