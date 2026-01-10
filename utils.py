from datetime import date

def get_week_type():
    week = date.today().isocalendar()[1]
    return "upper" if week % 2 == 0 else "lower"
