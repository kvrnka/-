import sqlite3
import os
import pandas as pd

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
            student_id = cursor.lastrowid
            from students_methods import update_id_of_student_from_list
            update_id_of_student_from_list(row["full_name"], row["group_number"], student_id)

        conn.commit()
        conn.close()

        return f"Успешно добавлено {len(df)} студентов!"
    except Exception as e:
        return f"Ошибка при обработке файла: {e}"


def get_students_by_group(group_number):
    create_db_list_of_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, group_number, full_name 
        FROM list_of_students 
        WHERE group_number = ?
        ORDER BY full_name ASC
    """, (group_number,))

    students = cursor.fetchall()
    conn.close()

    return [
        {"id": student[0], "group_number": student[1], "full_name": student[2]}
        for student in students
    ]


# def get_sorted_all_students():
#     create_db_list_of_student()
#     conn = sqlite3.connect(db_path)
#     cursor = conn.cursor()
#
#     cursor.execute("""
#     SELECT * FROM list_of_students
#     ORDER BY group_number ASC, full_name ASC
#     """)
#
#     students = cursor.fetchall()
#     conn.close()
#
#     return students


def get_unique_group_numbers():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT DISTINCT group_number FROM list_of_students
    ORDER BY group_number ASC
    """)

    groups = [row[0] for row in cursor.fetchall()]
    conn.close()

    return groups


def add_student_in_list(text):
    create_db_list_of_student()

    students = text.split('\n')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for student in students:
        name_and_group = student.split(", ")
        # 0 - имя, 1 - группа
        cursor.execute("INSERT OR IGNORE INTO list_of_students (group_number, full_name) VALUES (?, ?)",
                       (name_and_group[1], name_and_group[0]))
        student_id = cursor.lastrowid
        from students_methods import update_id_of_student_from_list
        update_id_of_student_from_list(name_and_group[0], name_and_group[1], student_id)

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


def get_student_from_list_by_id(id):
    create_db_list_of_student()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM list_of_students WHERE id = ?", (id,))
    student = cursor.fetchone()

    conn.close()
    return student


def get_id_from_list_by_name_and_group(name, group):
    create_db_list_of_student()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id FROM list_of_students
        WHERE full_name = ? AND group_number = ?
        """, (name, group))

    student = cursor.fetchone()
    conn.close()
    if student:
        return student[0]
    else:
        return None


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
