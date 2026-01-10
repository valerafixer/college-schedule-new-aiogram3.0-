from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from datetime import date, timedelta
import os

from config import TOKEN, ADMINS
from db import init_db, add_user, add_replacement, import_schedule, import_replacements
from states import ReplaceState
from scheduler import start_scheduler
from xlsx_parser import parse_schedule_xlsx, parse_replacements_xlsx

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("⏰ Напиши время рассылки в формате HH:MM (например 07:30)")


@dp.message_handler(regexp=r"\d{2}:\d{2}")
async def set_time(msg: types.Message):
    add_user(msg.from_user.id, msg.text)
    await msg.answer("✅ Время сохранено")


@dp.message_handler(commands=["replacement"])
async def replacement(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("✏️ Введите замену на завтра:")
    await ReplaceState.text.set()


@dp.message_handler(state=ReplaceState.text)
async def save_replace(msg: types.Message, state: FSMContext):
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    add_replacement(tomorrow, msg.text)
    await msg.answer("✅ Замена сохранена")
    await state.finish()


@dp.message_handler(commands=["load_schedule"])
async def load_schedule_command(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        return
    await msg.answer("📤 Отправьте XLSX файл с расписанием или заменами")


@dp.message_handler(content_types=['document'])
async def handle_document(msg: types.Message):
    if msg.from_user.id not in ADMINS:
        return
    
    file_name = msg.document.file_name
    
    if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
        await msg.answer("⚠️ Пожалуйста, отправьте XLSX файл")
        return
    
    # Скачиваем файл
    file = await bot.get_file(msg.document.file_id)
    file_path = f"temp_{file_name}"
    await bot.download_file(file.file_path, file_path)
    
    try:
        # Определяем тип файла по названию
        if 'schedule' in file_name.lower() or 'расписание' in file_name.lower():
            schedule_data = parse_schedule_xlsx(file_path)
            if schedule_data:
                import_schedule(schedule_data)
                await msg.answer(f"✅ Загружено {len(schedule_data)} записей расписания")
            else:
                await msg.answer("⚠️ Не удалось загрузить расписание. Проверьте формат файла.")
        
        elif 'replacement' in file_name.lower() or 'замен' in file_name.lower():
            replacements_data = parse_replacements_xlsx(file_path)
            if replacements_data:
                import_replacements(replacements_data)
                await msg.answer(f"✅ Загружено {len(replacements_data)} замен")
            else:
                await msg.answer("⚠️ Не удалось загрузить замены. Проверьте формат файла.")
        else:
            await msg.answer("⚠️ Не удалось определить тип файла.\nНазовите файл 'schedule.xlsx' или 'replacements.xlsx'")
    
    except Exception as e:
        await msg.answer(f"❌ Ошибка при обработке файла: {str(e)}")
    
    finally:
        # Удаляем временный файл
        if os.path.exists(file_path):
            os.remove(file_path)


if __name__ == "__main__":
    init_db()
    start_scheduler(bot)
    executor.start_polling(dp)