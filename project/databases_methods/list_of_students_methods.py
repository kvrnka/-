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
        group_number INTEGER,
        full_name TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_by_excel(file_path):
    create_db_list_of_student()
    try:
        df = pd.read_excel(file_path)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # очищаем бд перед тем как добавить новый список
        cursor.execute("DELETE FROM list_of_students")
        conn.commit()

        if "full_name" not in df.columns or "group_number" not in df.columns:
            return "Ошибка! В файле должны быть столбцы: 'full_name' и 'group_number'"

        for _, row in df.iterrows():
            cursor.execute("INSERT INTO list_of_students (full_name, group_number) VALUES (?, ?)",
                           (row["full_name"], row["group_number"]))

        conn.commit()
        conn.close()

        return f"Успешно добавлено {len(df)} студентов!"
    except Exception as e:
        return f"Ошибка при обработке файла: {e}"


def add_student_in_list(group_number, full_name):
    create_db_list_of_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO list_of_students (group_number, full_name) VALUES (?, ?)",
                   (group_number, full_name))

    conn.commit()
    conn.close()


def get_list_of_students():
    create_db_list_of_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM list_of_students")

    students = cursor.fetchall()

    conn.close()

    list_of_students = ''

    for i in range(len(students)):
        list_of_students += f"{students[i][0]}. " + students[i][2] + " " + str(students[i][1]) + '\n'

    return list_of_students


def get_student_from_list(id):
    create_db_list_of_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM list_of_students WHERE id = ?", (id,))
    student = cursor.fetchone()

    conn.close()
    return student

# можно передать список
def delete_student_from_list(ids):
    create_db_list_of_student()

    list_id = ids.split(", ")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    deleted_rows = 0

    for id in list_id:
        cursor.execute("DELETE FROM list_of_students WHERE id = ?", (id,))  # Удаляем запись
        conn.commit()
        deleted_rows += cursor.rowcount

    conn.close()

    return deleted_rows == len(list_id)

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
