from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu():
    """Главное меню с кнопками"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="📅 Расписание на сегодня", 
        callback_data="schedule_today"
    )
    builder.button(
        text="📆 Расписание на завтра", 
        callback_data="schedule_tomorrow"
    )
    builder.button(
        text="📋 Эта неделя", 
        callback_data="schedule_current_week"
    )
    builder.button(
        text="📋 Другая неделя", 
        callback_data="schedule_other_week"
    )
    builder.button(
        text="⚠️ Замены", 
        callback_data="replacements"
    )
    builder.button(
        text="⏰ Изменить время рассылки", 
        callback_data="change_time"
    )
    
    builder.adjust(2, 2, 1, 1)  # 2 в первой строке, 2 во второй, по 1 в остальных
    return builder.as_markup()


def get_week_menu(week_type):
    """Меню выбора дня недели"""
    builder = InlineKeyboardBuilder()
    
    days = [
        ("Понедельник", f"day_{week_type}_1"),
        ("Вторник", f"day_{week_type}_2"),
        ("Среда", f"day_{week_type}_3"),
        ("Четверг", f"day_{week_type}_4"),
        ("Пятница", f"day_{week_type}_5"),
        ("Суббота", f"day_{week_type}_6")
    ]
    
    for day_name, callback in days:
        builder.button(text=day_name, callback_data=callback)
    
    builder.button(text="◀️ Назад", callback_data="back_to_menu")
    
    builder.adjust(2, 2, 2, 1)  # 3 строки по 2 кнопки, затем 1 кнопка
    return builder.as_markup()


def get_replacements_menu():
    """Меню управления заменами (только для админов)"""
    builder = InlineKeyboardBuilder()
    
    builder.button(
        text="🗑 Удалить старые замены", 
        callback_data="delete_old_replacements"
    )
    builder.button(
        text="🗑 Очистить все замены", 
        callback_data="clear_all_replacements"
    )
    builder.button(
        text="◀️ Назад", 
        callback_data="back_to_menu"
    )
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder.as_markup()


def get_delete_replacement_menu(replacements):
    """Меню для выбора замены на удаление"""
    builder = InlineKeyboardBuilder()
    
    for repl_date, repl_text in replacements:
        # Показываем дату и начало текста
        preview = repl_text[:30] + "..." if len(repl_text) > 30 else repl_text
        button_text = f"🗑 {repl_date}: {preview}"
        builder.button(text=button_text, callback_data=f"del_repl_{repl_date}")
    
    builder.button(text="◀️ Назад", callback_data="replacements")
    
    builder.adjust(1)  # Все кнопки в один столбец
    return builder.as_markup()
