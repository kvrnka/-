import sqlite3
import os
import pandas as pd
from users_methods import get_user

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "list_of_students.db")


def create_db_list_of_student():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS list_of_students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_group INTEGER,
        full_name TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_by_excel(file_path):
    try:
        df = pd.read_excel(file_path)  # Загружаем файл
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Проверяем наличие нужных столбцов
        if "full_name" not in df.columns or "group_number" not in df.columns:
            return "Ошибка! В файле должны быть столбцы: 'full_name' и 'group_number'"

        # Добавляем студентов в базу данных
        for _, row in df.iterrows():
            cursor.execute("INSERT INTO list_of_students (full_name, group_number) VALUES (?, ?)",
                           (row["full_name"], row["group_number"]))

        conn.commit()
        conn.close()

        return f"Успешно добавлено {len(df)} студентов!"
    except Exception as e:
        return f"Ошибка при обработке файла: {e}"





# def add_student(tg_id, student_group):
#     create_db_list_of_student()
#
#     user = get_user(tg_id)
#     full_name = user[3]
#
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     cursor.execute("INSERT OR IGNORE INTO students (tg_id, student_group, full_name) VALUES (?, ?, ?)",
#                    (tg_id, student_group, full_name))
#
#     conn.commit()
#     conn.close()
#
#
# def get_student(tg_id):
#     create_db_list_of_student()
#
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT * FROM students WHERE tg_id = ?", (tg_id,))
#     student = cursor.fetchone()
#
#     conn.close()
#     return student
#
#
# def update_student_info(tg_id, new_group=None, new_full_name=None):
#     create_db_list_of_student()
#
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT * FROM students WHERE tg_id = ?", (tg_id,))
#     student = cursor.fetchone()
#
#     # студент не найден
#     if student is None:
#         conn.close()
#         return False
#
#     # Обновляем только те поля, которые переданы
#     update_fields = []
#     values = []
#
#     if new_group:
#         update_fields.append("student_group = ?")
#         values.append(new_group)
#     if new_full_name:
#         update_fields.append("full_name = ?")
#         values.append(new_full_name)
#
#     if update_fields:
#         values.append(tg_id)  # Добавляем tg_id в конец для WHERE
#         query = f"UPDATE students SET {', '.join(update_fields)} WHERE tg_id = ?"
#         cursor.execute(query, values)
#         conn.commit()
#         conn.close()
#         return True
#     else:
#         conn.close()
#         return False
