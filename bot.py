from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from datetime import date, timedelta, datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
import asyncio
import sys

from config import TOKEN, ADMINS
from db import (init_db, add_user, add_replacement, import_schedule, import_replacements, 
                get_schedule, get_replacement, get_all_replacements, delete_replacement, 
                delete_all_old_replacements, clear_replacements)
from states import ReplaceState
from scheduler import start_scheduler
from xlsx_parser import parse_schedule_xlsx, parse_replacements_xlsx
from keyboards import get_main_menu, get_week_menu, get_replacements_menu, get_delete_replacement_menu 
from utils import get_week_type, get_week_name, get_opposite_week

# Исправление для Python 3.10+
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Создаем event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

bot = Bot(TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage(), loop=loop)


@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    
    await msg.answer(
        f"👋 Добро пожаловать в бот расписания!\n\n"
        f"📅 Сейчас: {week_name} неделя\n\n"
        f"⏰ Напиши время рассылки в формате HH:MM (например 07:30)\n"
        f"Или используй меню ниже:",
        reply_markup=get_main_menu()
    )


@dp.message_handler(commands=["menu"])
async def menu(msg: types.Message):
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    await msg.answer(f"📱 Главное меню\n📅 Текущая неделя: {week_name}", reply_markup=get_main_menu())


@dp.message_handler(commands=["week"])
async def check_week(msg: types.Message):
    """Проверить тип текущей недели"""
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    
    today = date.today()
    days_since_monday = today.weekday()
    monday = today - timedelta(days=days_since_monday)
    week_number = monday.isocalendar()[1]
    
    await msg.answer(
        f"📅 Информация о текущей неделе:\n\n"
        f"Неделя: {week_name}\n"
        f"Номер недели в году: {week_number}\n"
        f"Понедельник: {monday.strftime('%d.%m.%Y')}"
    )


@dp.message_handler(regexp=r"\d{2}:\d{2}")
async def set_time(msg: types.Message):
    add_user(msg.from_user.id, msg.text)
    await msg.answer("✅ Время сохранено", reply_markup=get_main_menu())


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
    await msg.answer("✅ Замена сохранена", reply_markup=get_main_menu())
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
    
    file = await bot.get_file(msg.document.file_id)
    file_path = f"temp_{file_name}"
    await bot.download_file(file.file_path, file_path)
    
    try:
        if 'schedule' in file_name.lower() or 'расписание' in file_name.lower():
            schedule_data = parse_schedule_xlsx(file_path)
            if schedule_data:
                import_schedule(schedule_data)
                await msg.answer(f"✅ Загружено {len(schedule_data)} записей расписания", reply_markup=get_main_menu())
            else:
                await msg.answer("⚠️ Не удалось загрузить расписание. Проверьте формат файла.")
        
        elif 'replacement' in file_name.lower() or 'замен' in file_name.lower():
            replacements_data = parse_replacements_xlsx(file_path)
            if replacements_data:
                import_replacements(replacements_data)
                await msg.answer(f"✅ Загружено {len(replacements_data)} замен", reply_markup=get_main_menu())
            else:
                await msg.answer("⚠️ Не удалось загрузить замены. Проверьте формат файла.")
        else:
            await msg.answer("⚠️ Не удалось определить тип файла.\nНазовите файл 'schedule.xlsx' или 'replacements.xlsx'")
    
    except Exception as e:
        await msg.answer(f"❌ Ошибка при обработке файла: {str(e)}")
    
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


# Обработчики кнопок
@dp.callback_query_handler(lambda c: c.data == "schedule_today")
async def show_today_schedule(callback: types.CallbackQuery):
    await callback.answer()
    
    today = datetime.now()
    weekday = today.isoweekday()
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    today_date = today.strftime("%Y-%m-%d")
    
    # Проверяем замены
    replacement = get_replacement(today_date)
    if replacement:
        text = f"⚠️ Замены на сегодня ({today.strftime('%d.%m.%Y')}):\n\n{replacement}"
        await callback.message.answer(text, reply_markup=get_main_menu())
        return
    
    # Получаем расписание
    lessons = get_schedule(week_type, weekday)
    
    if not lessons:
        await callback.message.answer("📭 На сегодня нет расписания", reply_markup=get_main_menu())
        return
    
    days_names = ["", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    text = f"📚 Расписание на сегодня\n{days_names[weekday]}, {week_name} неделя\n\n"
    for i, subj in lessons:
        text += f"{i}. {subj}\n"
    
    await callback.message.answer(text, reply_markup=get_main_menu())


@dp.callback_query_handler(lambda c: c.data == "schedule_tomorrow")
async def show_tomorrow_schedule(callback: types.CallbackQuery):
    await callback.answer()
    
    tomorrow = datetime.now() + timedelta(days=1)
    weekday = tomorrow.isoweekday()
    week_type = get_week_type(tomorrow.date())
    week_name = get_week_name(week_type)
    tomorrow_date = tomorrow.strftime("%Y-%m-%d")
    
    # Проверяем замены
    replacement = get_replacement(tomorrow_date)
    if replacement:
        text = f"⚠️ Замены на завтра ({tomorrow.strftime('%d.%m.%Y')}):\n\n{replacement}"
        await callback.message.answer(text, reply_markup=get_main_menu())
        return
    
    # Получаем расписание
    lessons = get_schedule(week_type, weekday)
    
    if not lessons:
        await callback.message.answer("📭 На завтра нет расписания", reply_markup=get_main_menu())
        return
    
    days_names = ["", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    
    text = f"📚 Расписание на завтра\n{days_names[weekday]}, {week_name} неделя\n\n"
    for i, subj in lessons:
        text += f"{i}. {subj}\n"
    
    await callback.message.answer(text, reply_markup=get_main_menu())


@dp.callback_query_handler(lambda c: c.data == "schedule_current_week")
async def show_current_week_menu(callback: types.CallbackQuery):
    await callback.answer()
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    
    await callback.message.answer(
        f"📅 Выберите день недели\n{week_name.capitalize()} неделя:",
        reply_markup=get_week_menu(week_type)
    )


@dp.callback_query_handler(lambda c: c.data == "schedule_other_week")
async def show_other_week_menu(callback: types.CallbackQuery):
    await callback.answer()
    current_week_type = get_week_type()
    other_week_type = get_opposite_week(current_week_type)
    week_name = get_week_name(other_week_type)
    
    await callback.message.answer(
        f"📅 Выберите день недели\n{week_name.capitalize()} неделя:",
        reply_markup=get_week_menu(other_week_type)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("day_"))
async def show_day_schedule(callback: types.CallbackQuery):
    await callback.answer()
    
    parts = callback.data.split("_")
    week_type = parts[1]
    weekday = int(parts[2])
    
    lessons = get_schedule(week_type, weekday)
    
    days_names = ["", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
    week_name = get_week_name(week_type)
    
    if not lessons:
        text = f"📭 На {days_names[weekday].lower()}\n({week_name} неделя)\nнет расписания"
    else:
        text = f"📚 Расписание на {days_names[weekday].lower()}\n{week_name.capitalize()} неделя\n\n"
        for i, subj in lessons:
            text += f"{i}. {subj}\n"
    
    await callback.message.answer(text, reply_markup=get_week_menu(week_type))


@dp.callback_query_handler(lambda c: c.data == "replacements")
async def show_replacements(callback: types.CallbackQuery):
    await callback.answer()
    
    replacements = get_all_replacements()
    
    if not replacements:
        text = "✅ Замен нет"
        # Для админов показываем меню управления
        if callback.from_user.id in ADMINS:
            await callback.message.answer(text, reply_markup=get_replacements_menu())
        else:
            await callback.message.answer(text, reply_markup=get_main_menu())
        return
    
    text = "⚠️ Актуальные замены:\n\n"
    for repl_date, repl_text in replacements:
        date_obj = datetime.strptime(repl_date, "%Y-%m-%d")
        text += f"📅 {date_obj.strftime('%d.%m.%Y')}:\n{repl_text}\n\n"
    
    # Для админов добавляем кнопки управления
    if callback.from_user.id in ADMINS:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("🗑 Удалить замену", callback_data="select_replacement_to_delete"),
            InlineKeyboardButton("🗑 Удалить старые замены", callback_data="delete_old_replacements"),
            InlineKeyboardButton("🗑 Очистить все замены", callback_data="clear_all_replacements"),
            InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
        )
        await callback.message.answer(text, reply_markup=keyboard)
    else:
        await callback.message.answer(text, reply_markup=get_main_menu())


@dp.callback_query_handler(lambda c: c.data == "select_replacement_to_delete")
async def select_replacement_to_delete(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    replacements = get_all_replacements()
    
    if not replacements:
        await callback.answer("✅ Замен нет", show_alert=True)
        return
    
    await callback.message.answer(
        "🗑 Выберите замену для удаления:",
        reply_markup=get_delete_replacement_menu(replacements)
    )


@dp.callback_query_handler(lambda c: c.data.startswith("del_repl_"))
async def delete_selected_replacement(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    repl_date = callback.data.replace("del_repl_", "")
    
    if delete_replacement(repl_date):
        await callback.answer("✅ Замена удалена", show_alert=True)
        
        # Показываем обновленный список
        replacements = get_all_replacements()
        if replacements:
            await callback.message.edit_text(
                "🗑 Выберите замену для удаления:",
                reply_markup=get_delete_replacement_menu(replacements)
            )
        else:
            await callback.message.edit_text(
                "✅ Все замены удалены",
                reply_markup=get_replacements_menu()
            )
    else:
        await callback.answer("❌ Не удалось удалить замену", show_alert=True)


@dp.callback_query_handler(lambda c: c.data == "delete_old_replacements")
async def delete_old_replacements_handler(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    count = delete_all_old_replacements()
    await callback.answer(f"✅ Удалено старых замен: {count}", show_alert=True)
    
    # Обновляем список замен
    await show_replacements(callback)


@dp.callback_query_handler(lambda c: c.data == "clear_all_replacements")
async def clear_all_replacements_handler(callback: types.CallbackQuery):
    await callback.answer()
    
    if callback.from_user.id not in ADMINS:
        await callback.answer("❌ Доступно только администраторам", show_alert=True)
        return
    
    clear_replacements()
    await callback.answer("✅ Все замены удалены", show_alert=True)
    await callback.message.answer("✅ Все замены удалены", reply_markup=get_main_menu())


@dp.callback_query_handler(lambda c: c.data == "change_time")
async def change_time(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("⏰ Напишите новое время рассылки в формате HH:MM (например 07:30)")


@dp.callback_query_handler(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.answer()
    week_type = get_week_type()
    week_name = get_week_name(week_type)
    await callback.message.answer(f"📱 Главное меню\n📅 Текущая неделя: {week_name}", reply_markup=get_main_menu())


async def on_startup(dispatcher):
    """Вызывается при запуске бота"""
    init_db()
    start_scheduler(bot)
    print("✅ Бот запущен!")


async def on_shutdown(dispatcher):
    """Вызывается при остановке бота"""
    print("🛑 Бот остановлен!")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=on_shutdown)
