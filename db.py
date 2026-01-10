import sqlite3

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

def init_db():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        send_time TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS schedule (
        week_type TEXT,
        weekday INTEGER,
        lesson_order INTEGER,
        subject TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS replacements (
        date TEXT,
        text TEXT
    )
    """)

    conn.commit()


def add_user(user_id, time):
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, send_time) VALUES (?, ?)",
        (user_id, time)
    )
    conn.commit()


def get_users():
    cursor.execute("SELECT user_id, send_time FROM users WHERE active=1")
    return cursor.fetchall()


def get_schedule(week_type, weekday):
    cursor.execute("""
    SELECT lesson_order, subject FROM schedule
    WHERE week_type=? AND weekday=?
    ORDER BY lesson_order
    """, (week_type, weekday))
    return cursor.fetchall()


def add_replacement(date, text):
    cursor.execute("INSERT INTO replacements VALUES (?, ?)", (date, text))
    conn.commit()


def get_replacement(date):
    cursor.execute("SELECT text FROM replacements WHERE date=?", (date,))
    row = cursor.fetchone()
    return row[0] if row else None


def clear_schedule():
    """Очищает таблицу расписания"""
    cursor.execute("DELETE FROM schedule")
    conn.commit()


def import_schedule(schedule_data):
    """Импортирует расписание из списка кортежей"""
    clear_schedule()
    cursor.executemany(
        "INSERT INTO schedule (week_type, weekday, lesson_order, subject) VALUES (?, ?, ?, ?)",
        schedule_data
    )
    conn.commit()


def clear_replacements():
    """Очищает таблицу замен"""
    cursor.execute("DELETE FROM replacements")
    conn.commit()


def import_replacements(replacements_data):
    """Импортирует замены из списка кортежей"""
    cursor.executemany(
        "INSERT INTO replacements (date, text) VALUES (?, ?)",
        replacements_data
    )
    conn.commit()