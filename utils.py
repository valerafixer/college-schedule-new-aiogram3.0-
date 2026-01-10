from datetime import date, datetime, timedelta


def get_week_type(check_date=None):
    """
    Определяет тип недели (верхняя/нижняя) по дате понедельника
    
    Теперь:
    Чётная неделя  → верхняя
    Нечётная неделя → нижняя
    """
    if check_date is None:
        check_date = date.today()
    elif isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    
    # Находим понедельник текущей недели
    days_since_monday = check_date.weekday()  # 0 = понедельник, 6 = воскресенье
    monday = check_date - timedelta(days=days_since_monday)
    
    # Номер недели в году (ISO)
    week_number = monday.isocalendar()[1]
    
    # Самое важное изменение:
    # Чётная неделя → "upper" (верхняя)
    # Нечётная неделя → "lower" (нижняя)
    return "upper" if week_number % 2 == 0 else "lower"


def get_week_name(week_type):
    """Возвращает красивое название недели"""
    if week_type == "upper":
        return "верхняя (чётная)"
    else:
        return "нижняя (нечётная)"


def get_opposite_week(week_type):
    """Возвращает противоположный тип недели"""
    return "lower" if week_type == "upper" else "upper"
