import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "../databases")
os.makedirs(DATABASE_DIR, exist_ok = True)

db_path = os.path.join(DATABASE_DIR, "tasks.db")


def create_db_task():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицу, если её нет
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        primary_key INTEGER PRIMARY KEY AUTOINCREMENT,
        name_of_task TEXT,
        deadline TEXT,
        target_groups TEXT,
        date_of_creation TEXT,
        is_public INTEGER
    )
    """)

    conn.commit()
    conn.close()


def add_task(name_of_task, deadline, target_groups):
    create_db_task()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    date_of_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Добавляем новую запись
    cursor.execute("""
            INSERT INTO tasks (name_of_task, deadline, target_groups, date_of_creation, is_public)
            VALUES (?, ?, ?, ?, ?)
        """, (name_of_task, deadline, target_groups, date_of_creation, 0))
    primary_key = cursor.lastrowid

    conn.commit()
    conn.close()

    return primary_key


def get_unpublished_tasks():
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tasks WHERE is_public = 0
    """)

    tasks = cursor.fetchall()
    conn.close()

    def parse_deadline(task):
        return datetime.strptime(task[2], "%d.%m.%Y %H:%M")

    sorted_tasks = sorted(tasks, key = parse_deadline)

    return sorted_tasks


def get_published_tasks():
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tasks WHERE is_public = 1
    """)

    tasks = cursor.fetchall()
    conn.close()

    def parse_deadline(task):
        return datetime.strptime(task[2], "%d.%m.%Y %H:%M")

    sorted_tasks = sorted(tasks, key = parse_deadline)

    return sorted_tasks


def get_task_by_pk(primary_key):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Получаем запись по ID
    cursor.execute("""
        SELECT * FROM tasks WHERE primary_key = ?
    """, (primary_key,))

    task = cursor.fetchone()

    conn.close()

    return task


def make_public(pk):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
            UPDATE tasks
            SET is_public = 1
            WHERE primary_key = ?
            """, (pk,))

    conn.commit()
    conn.close()


def update_task_deadline(task_id, new_deadline):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE tasks
    SET deadline = ?
    WHERE primary_key = ?
    """, (new_deadline, task_id))

    conn.commit()
    conn.close()


def delete_task(task_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Удаляем задание по его id
    cursor.execute("""
    DELETE FROM tasks
    WHERE primary_key = ?
    """, (task_id,))

    conn.commit()
    conn.close()
