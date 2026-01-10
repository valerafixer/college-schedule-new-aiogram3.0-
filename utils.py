from datetime import date, datetime, timedelta

def get_week_type(check_date=None):
    """
    Определяет тип недели (верхняя/нижняя) по дате понедельника
    Нижняя неделя = чётная неделя
    Верхняя неделя = нечётная неделя
    """
    if check_date is None:
        check_date = date.today()
    elif isinstance(check_date, str):
        check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
    
    # Находим понедельник текущей недели
    days_since_monday = check_date.weekday()  # 0 = понедельник
    monday = check_date - timedelta(days=days_since_monday)
    
    # Получаем номер недели года для этого понедельника
    week_number = monday.isocalendar()[1]
    
    # Чётная неделя = нижняя, нечётная = верхняя
    return "lower" if week_number % 2 == 0 else "upper"


def get_week_name(week_type):
    """Возвращает название недели"""
    return "верхняя (нечётная)" if week_type == "upper" else "нижняя (чётная)"


def get_opposite_week(week_type):
    """Возвращает противоположный тип недели"""
    return "lower" if week_type == "upper" else "upper"