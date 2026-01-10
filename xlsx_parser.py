from openpyxl import load_workbook
from datetime import datetime

def parse_schedule_xlsx(file_path):
    """
    Парсит XLSX файл с расписанием
    Ожидаемая структура:
    Столбцы: Тип недели | День недели | Номер урока | Предмет
    или
    Лист 1: Верхняя неделя, Лист 2: Нижняя неделя
    Строки - дни недели, столбцы - номера уроков
    """
    try:
        wb = load_workbook(file_path)
        schedule_data = []
        
        # Вариант 1: Один лист с колонками
        if len(wb.sheetnames) == 1 or 'Расписание' in wb.sheetnames:
            ws = wb.active if len(wb.sheetnames) == 1 else wb['Расписание']
            
            for row in ws.iter_rows(min_row=2, values_only=True):
                if not any(row):
                    continue
                
                week_type = str(row[0]).lower() if row[0] else None
                weekday = int(row[1]) if row[1] else None
                lesson_order = int(row[2]) if row[2] else None
                subject = str(row[3]) if row[3] else None
                
                if all([week_type, weekday, lesson_order, subject]):
                    # Преобразуем "верхняя"/"нижняя" в "upper"/"lower"
                    if week_type in ['верхняя', 'верх']:
                        week_type = 'upper'
                    elif week_type in ['нижняя', 'низ']:
                        week_type = 'lower'
                    
                    schedule_data.append((week_type, weekday, lesson_order, subject))
        
        # Вариант 2: Два листа (Верхняя неделя и Нижняя неделя)
        else:
            week_mapping = {
                'Верхняя неделя': 'upper',
                'Нижняя неделя': 'lower',
                'Upper': 'upper',
                'Lower': 'lower'
            }
            
            for sheet_name in wb.sheetnames:
                week_type = None
                for key, value in week_mapping.items():
                    if key.lower() in sheet_name.lower():
                        week_type = value
                        break
                
                if not week_type:
                    continue
                
                ws = wb[sheet_name]
                
                # Читаем расписание (строки = дни, столбцы = уроки)
                for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
                    if not any(row):
                        continue
                    
                    weekday = row_idx
                    if weekday > 7:
                        break
                    
                    for lesson_order, subject in enumerate(row[1:], start=1):
                        if subject and str(subject).strip():
                            schedule_data.append((week_type, weekday, lesson_order, str(subject).strip()))
        
        return schedule_data
    
    except Exception as e:
        print(f"Ошибка парсинга расписания: {e}")
        return []


def parse_replacements_xlsx(file_path):
    """
    Парсит XLSX файл с заменами
    Ожидаемая структура:
    Столбцы: Дата | Текст замены
    """
    try:
        wb = load_workbook(file_path)
        ws = wb.active
        
        replacements_data = []
        
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not any(row):
                continue
            
            date_val = row[0]
            text = str(row[1]) if row[1] else None
            
            if not text:
                continue
            
            # Обработка даты
            if isinstance(date_val, datetime):
                date_str = date_val.strftime('%Y-%m-%d')
            elif isinstance(date_val, str):
                try:
                    # Попытка распарсить дату из строки
                    parsed_date = datetime.strptime(date_val, '%Y-%m-%d')
                    date_str = parsed_date.strftime('%Y-%m-%d')
                except:
                    try:
                        parsed_date = datetime.strptime(date_val, '%d.%m.%Y')
                        date_str = parsed_date.strftime('%Y-%m-%d')
                    except:
                        continue
            else:
                continue
            
            replacements_data.append((date_str, text))
        
        return replacements_data
    
    except Exception as e:
        print(f"Ошибка парсинга замен: {e}")
        return []