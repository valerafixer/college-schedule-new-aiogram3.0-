from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """Главное меню с кнопками"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("📅 Расписание на сегодня", callback_data="schedule_today"),
        InlineKeyboardButton("📆 Расписание на завтра", callback_data="schedule_tomorrow")
    )
    keyboard.add(
        InlineKeyboardButton("📋 Эта неделя", callback_data="schedule_current_week"),
        InlineKeyboardButton("📋 Другая неделя", callback_data="schedule_other_week")
    )
    keyboard.add(
        InlineKeyboardButton("⚠️ Замены", callback_data="replacements")
    )
    keyboard.add(
        InlineKeyboardButton("⏰ Изменить время рассылки", callback_data="change_time")
    )
    return keyboard

def get_week_menu(week_type):
    """Меню выбора дня недели"""
    keyboard = InlineKeyboardMarkup(row_width=2)
    days = [
        ("Понедельник", f"day_{week_type}_1"),
        ("Вторник", f"day_{week_type}_2"),
        ("Среда", f"day_{week_type}_3"),
        ("Четверг", f"day_{week_type}_4"),
        ("Пятница", f"day_{week_type}_5"),
        ("Суббота", f"day_{week_type}_6")
    ]
    for day_name, callback in days:
        keyboard.add(InlineKeyboardButton(day_name, callback_data=callback))
    
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu"))
    return keyboard


def get_replacements_menu():
    """Меню управления заменами (только для админов)"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("🗑 Удалить старые замены", callback_data="delete_old_replacements"),
        InlineKeyboardButton("🗑 Очистить все замены", callback_data="clear_all_replacements"),
        InlineKeyboardButton("◀️ Назад", callback_data="back_to_menu")
    )
    return keyboard


def get_delete_replacement_menu(replacements):
    """Меню для выбора замены на удаление"""
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for repl_date, repl_text in replacements:
        # Показываем дату и начало текста
        preview = repl_text[:30] + "..." if len(repl_text) > 30 else repl_text
        button_text = f"🗑 {repl_date}: {preview}"
        keyboard.add(InlineKeyboardButton(button_text, callback_data=f"del_repl_{repl_date}"))
    
    keyboard.add(InlineKeyboardButton("◀️ Назад", callback_data="replacements"))
    return keyboard