from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime
from db import get_users, get_schedule, get_replacement
from utils import get_week_type

scheduler = AsyncIOScheduler()

def start_scheduler(bot):
    """Запускает планировщик задач"""
    if not scheduler.running:
        scheduler.add_job(send_all, "interval", minutes=1, args=[bot])
        scheduler.start()
        print("Планировщик запущен!")

async def send_all(bot):
    """Отправляет расписание всем пользователям в установленное время"""
    now = datetime.now().strftime("%H:%M")
    weekday = datetime.now().isoweekday()
    week_type = get_week_type()
    
    today_date = datetime.now().strftime("%Y-%m-%d")

    for user_id, time in get_users():
        if time != now:
            continue

        # Проверяем замены на сегодня
        replacement = get_replacement(today_date)
        if replacement:
            text = f"⚠️ Замены на сегодня:\n{replacement}\n\n"
            try:
                await bot.send_message(user_id, text)
            except Exception as e:
                print(f"Ошибка отправки замены пользователю {user_id}: {e}")
            continue

        # Получаем обычное расписание
        lessons = get_schedule(week_type, weekday)
        if not lessons:
            continue

        text = "📚 Расписание на сегодня:\n"
        for i, subj in lessons:
            text += f"{i}. {subj}\n"

        try:
            await bot.send_message(user_id, text)
        except Exception as e:
            print(f"Ошибка отправки расписания пользователю {user_id}: {e}")
