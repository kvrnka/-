import sqlite3
import os
from users_methods import get_user
from list_of_students_methods import get_id_from_list_by_name_and_group

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "students.db")


def create_db_student():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        tg_id INTEGER UNIQUE,
        student_group INTEGER,
        full_name TEXT,
        id_from_list INTEGER
    )
    """)

    conn.commit()
    conn.close()


def add_student(tg_id, student_group):
    create_db_student()

    user = get_user(tg_id)
    full_name = user[3]
    id_from_list = get_id_from_list_by_name_and_group(full_name, student_group)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    if id_from_list != None:
        cursor.execute(
            "INSERT OR IGNORE INTO students (tg_id, student_group, full_name, id_from_list) VALUES (?, ?, ?, ?)",
            (tg_id, student_group, full_name, id_from_list))
        conn.commit()
        conn.close()
        return True
    else:
        cursor.execute(
            "INSERT OR IGNORE INTO students (tg_id, student_group, full_name) VALUES (?, ?, ?)",
            (tg_id, student_group, full_name))
        conn.commit()
        conn.close()
        return False


def get_student_by_tg_id(tg_id):
    create_db_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE tg_id = ?", (tg_id,))
    student = cursor.fetchone()

    conn.close()
    return student


def update_id_of_student_from_list(name, group, id_from_list):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE full_name = ? AND student_group = ?",
        (name, group)
    )
    student = cursor.fetchone()
    if student:
        cursor.execute("UPDATE students SET id_from_list = ? WHERE tg_id = ?", (id_from_list, student[0]))
        conn.commit()
    conn.close()


def update_student_info(tg_id, new_group = None, new_full_name = None):
    create_db_student()  # Убеждаемся, что БД существует

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем текущие данные студента
    cursor.execute("SELECT * FROM students WHERE tg_id = ?", (tg_id,))
    student = cursor.fetchone()

    if student is None:
        conn.close()
        return [False, False]  # Студент не найден

    # Собираем поля для обновления
    update_fields = []
    values = []

    if new_group is not None:
        update_fields.append("student_group = ?")
        values.append(new_group)
    if new_full_name is not None:
        update_fields.append("full_name = ?")
        values.append(new_full_name)

    # Если есть, что обновлять — выполняем UPDATE
    if update_fields:
        values.append(tg_id)  # tg_id для WHERE
        query = f"UPDATE students SET {', '.join(update_fields)} WHERE tg_id = ?"
        cursor.execute(query, values)
        conn.commit()

    # Получаем обновленные данные студента
    cursor.execute("SELECT full_name, student_group FROM students WHERE tg_id = ?", (tg_id,))
    updated_student = cursor.fetchone()

    if updated_student:
        updated_name, updated_group = updated_student

        # Проверяем, есть ли студент в списке лектора
        number = get_id_from_list_by_name_and_group(updated_name, updated_group)

        # Обновляем id_from_list (может быть числом или NULL)
        cursor.execute("UPDATE students SET id_from_list = ? WHERE tg_id = ?", (number, tg_id))
        conn.commit()
        conn.close()

        return [True,
                number is not None]  # первый аргумент значит, что пользователь обновлен, второй - найден ли пользователь в списке лектора

    conn.close()
    return [False, False]  # Обновление не произошло
