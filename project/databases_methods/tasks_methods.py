import sqlite3
import os
import shutil
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


def is_unique_task(task_name):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM tasks WHERE name_of_task = ? LIMIT 1", (task_name,))
    result = cursor.fetchone()

    conn.close()
    if result:
        # название не уникально
        return False
    return True


def parse_deadline(task):
    return datetime.strptime(task[2], "%d.%m.%Y %H:%M")


def from_list_to_task_text(tasks):
    sorted_tasks = sorted(tasks, key = parse_deadline)
    text = ''
    for task in sorted_tasks:
        text += f'Название работы: {task[1]}\nДедлайн: {task[2]}\nГруппы: {task[3]}\nНомер: {task[0]}\n\n'
    return text


def get_unpublished_tasks():
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tasks WHERE is_public = 0
    """)

    tasks = cursor.fetchall()
    conn.close()

    text = from_list_to_task_text(tasks)
    return text


def get_publish_task_for_student_by_group(group):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
            SELECT * FROM tasks 
            WHERE is_public = 1 
            AND (target_groups = 'все' OR instr(target_groups, ?) > 0)
        """, (str(group),))

    tasks = cursor.fetchall()
    conn.close()

    text = from_list_to_task_text(tasks)
    return text


def get_published_tasks():
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM tasks WHERE is_public = 1
    """)

    tasks = cursor.fetchall()
    conn.close()

    text = from_list_to_task_text(tasks)
    return text


def get_task_for_admin(groups):
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    groups_list = [group.strip() for group in groups.split(',')]
    query = """
        SELECT * FROM tasks
        WHERE is_public = 1 AND (
            target_groups = 'все' OR
            {} 
        )
        """.format(' OR '.join([f"target_groups LIKE ?" for _ in groups_list]))

    params = tuple([f"%{group}%" for group in groups_list])
    cursor.execute(query, params)
    tasks = cursor.fetchall()

    conn.close()
    text = from_list_to_task_text(tasks)
    return text


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
    create_db_task()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name_of_task FROM tasks WHERE primary_key = ?", (task_id,))
    result = cursor.fetchone()

    cursor.execute("""
        DELETE FROM tasks
        WHERE primary_key = ?
        """, (task_id,))

    conn.commit()
    conn.close()

    if result:
        task_name = result[0]
        task_dir = os.path.join(BASE_DIR, "..", "task")
        task_folder = os.path.join(task_dir, task_name)
        if os.path.exists(task_folder):
            try:
                shutil.rmtree(task_folder)
            except Exception as e:
                print(f"Ошибка при удалении папки '{task_folder}': {e}")
        else:
            print(f"Ошибка: Папка '{task_folder}' не найдена.")
