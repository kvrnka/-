import sqlite3
import os
from users_methods import get_user
from students_methods import get_student_by_tg_id

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "admins.db")


def create_db_admin():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        tg_id INTEGER UNIQUE,
        tg_username TEXT,
        full_name TEXT,
        groups_of_students TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_admin(tg_id, tg_username, groups_of_students):
    create_db_admin()

    user = get_user(tg_id)
    student = get_student_by_tg_id(tg_id)
    if student:
        full_name = student[2]
    else:
        full_name = user[3]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("INSERT OR IGNORE INTO admins (tg_id, tg_username, full_name, groups_of_students) "
                   "VALUES (?, ?, ?, ?)",
                   (tg_id, tg_username, full_name, groups_of_students))

    conn.commit()
    conn.close()


def get_admin(tg_id):
    create_db_admin()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admins WHERE tg_id = ?", (tg_id,))
    admin = cursor.fetchone()

    conn.close()
    return admin


def delete_admin_by_username(tg_usernames):
    create_db_admin()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    tg_user = [user.strip() for user in tg_usernames.split(",")]

    deleted_rows = 0

    for user in tg_user:
        cursor.execute("DELETE FROM admins WHERE tg_username = ?", (user,))
        conn.commit()
        deleted_rows += cursor.rowcount

    conn.close()

    return deleted_rows, len(tg_user)


def get_all_admin():
    create_db_admin()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admins")

    admins = cursor.fetchall()

    conn.close()

    list_of_admin = ''

    for i in range(len(admins)):
        list_of_admin += f"{i + 1}. Имя пользователя: @" + admins[i][1] + '\n'
        list_of_admin += "Имя: " + admins[i][2] + '\n'
        list_of_admin += "Группы: " + admins[i][3] + '\n'
        list_of_admin += '\n'

    return list_of_admin


def update_admin_info(tg_id, new_groups_of_students=None, new_full_name=None):
    create_db_admin()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admins WHERE tg_id = ?", (tg_id,))
    admin = cursor.fetchone()

    # админ не найден
    if admin is None:
        conn.close()
        return False

    # Обновляем только те поля, которые переданы
    update_fields = []
    values = []

    if new_groups_of_students:
        update_fields.append("groups_of_students = ?")
        values.append(new_groups_of_students)
    if new_full_name:
        update_fields.append("full_name = ?")
        values.append(new_full_name)

    if update_fields:
        values.append(tg_id)
        query = f"UPDATE admins SET {', '.join(update_fields)} WHERE tg_id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False
