import random
import sympy as sp
import subprocess
import os
from databases_methods.list_of_students_methods import get_students_by_group


def from_equations_to_latex(equations):
    latex_code = (
            r'\[' + '\n'
                    r'\begin{cases}' + '\n'
    )
    for eq in equations:
        latex_code += sp.latex(eq) + r' \\' + '\n'
    latex_code += (
            r'\end{cases}' + '\n'
                             r'\]' + '\n'
    )
    return latex_code


# функция для определения пропорциональности строк, чтобы не допускать зануления строки
def is_proportional(ai, row):
    relation = 0
    for ai_elem, row_elem in zip(ai, row):
        if ai_elem == 0 and row_elem == 0:
            continue
        elif ai_elem == 0 and row_elem != 0 or ai_elem != 0 and row_elem == 0:
            return False
        else:
            ratio = ai_elem / row_elem
            if relation == 0:
                relation = ratio
            elif relation != ratio:
                return False
    return True


# функция для генерации заданий для одного варианта
def generate_eq_for_variant(count_of_task, count_of_eq):
    latex_code_one_variants = ''
    latex_code_ans = ''
    for task in range(count_of_task):
        x_ans = [random.randint(-15, 15) for _ in range(count_of_eq[task])]  # генерируем ответ
        while x_ans == [0] * count_of_eq[task]:
            x_ans = [random.randint(-10, 10) for _ in range(count_of_eq[task])]
        A = []  # матрица коэффицентов
        b = []

        for i in range(count_of_eq[task]):
            ai = [random.randint(-10, 10) for _ in range(count_of_eq[task])]
            # не допускаем, чтобы строки были пропорциональны
            for row in A:
                while is_proportional(ai, row) or ai == [0] * count_of_eq[task]:
                    ai = [random.randint(-10, 10) for _ in range(count_of_eq[task])]
            bi = sum(a * x for a, x in zip(ai, x_ans))
            b.append(bi)
            A.append(ai)

        A_matrix = sp.Matrix(A)
        b_vector = sp.Matrix(b)

        x_i = sp.symbols(f'x1:{count_of_eq[task] + 1}')
        x_vector = sp.Matrix(x_i)
        equations = [sp.Eq(lhs, rhs) for lhs, rhs in zip(A_matrix * x_vector, b_vector)]

        task_tex = from_equations_to_latex(equations)
        latex_code_one_variants += rf'Задание {task + 1}.\\' + '\n'
        latex_code_one_variants += task_tex + '\n'

        vector_string = r'$ ('

        for elem in x_ans:
            vector_string += rf'{elem},'

        vector_string = vector_string[:-1] + r') $'

        latex_code_ans += (
                rf'{task + 1}.' + '\n'
                + vector_string + '\n'
        )

    return latex_code_one_variants, latex_code_ans


# def generate_tex(task_info, count_of_task, count_of_eq):
#     latex_code_for_all_task = (
#             r'\documentclass[a4paper,12pt]{article}' + '\n'
#                                                        r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
#                                                                                                   r'\usepackage[T1,T2A]{fontenc}' + '\n'
#                                                                                                                                     r'\usepackage[utf8]{inputenc}' + '\n'
#                                                                                                                                                                      r'\usepackage[english, russian]{babel}' + '\n'
#                                                                                                                                                                                                                r'\begin{document}' + '\n'
#     )
#     latex_code_for_all_answers = latex_code_for_all_task
#     latex_code_for_all_answers += (
#             r'\begin{center}' + '\n'
#                                 r'Ответы' + '\n'
#                                             r'\end{center}' + '\n'
#                                                               '\n'
#     )
#
#     # count_of_task - список, где на i-ом месте стоит размер i+1 системы
#     # task_info - информация из бд
#
#     group = task_info[3]
#     cnt_of_students = 0
#
#     # if group == 'все':
#     #     # groups =
#     #     pass
#     # else:
#     #     groups = group.split(", ")
#
#     groups = group.split(", ")
#
#     for group_of_students in groups:
#         students = get_students_by_group(
#             int(group_of_students))  # получаем студентов из группы в алфавитном порядке
#         cnt_of_students += len(students)
#         for student in students:
#             name_of_variant = (
#                     r'\begin{center}' + '\n'
#                                         rf'\textbf{{Вариант --- {student["full_name"]}}}' + '\n'
#                                                                                             r'\end{center}' + '\n'
#                                                                                                               '\n'
#             )
#             latex_code_for_all_task += name_of_variant
#             latex_code_for_all_answers += name_of_variant
#
#             task_latex, ans_latex = generate_eq_for_variant(count_of_task, count_of_eq)
#             latex_code_for_all_task += task_latex + r'\newpage'
#             latex_code_for_all_answers += ans_latex
#
#     latex_code_for_all_task += r'\end{document}' + '\n'
#     latex_code_for_all_answers += r'\end{document}' + '\n'
#     return latex_code_for_all_task, latex_code_for_all_answers
#
#
# def generate_pdf(task_info, count_of_task, count_of_eq):
#     task_name = task_info[1]
#     task_folder = os.path.join("task", task_name)
#
#     # Если папка с таким названием не существует, создаем её
#     if not os.path.exists(task_folder):
#         os.makedirs(task_folder)
#
#     latex_code, latex_code_for_ans = generate_tex(task_info, count_of_task, count_of_eq)
#
#     tex_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations.tex")
#     tex_ans_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations_answer.tex")
#
#     with open(tex_file_path, "w") as file:
#         file.write(latex_code)
#
#     with open(tex_ans_file_path, "w") as file:
#         file.write(latex_code_for_ans)
#
#     # Запускаем компиляцию PDF для каждого файла в нужной директории
#     subprocess.run(["pdflatex", "-output-directory", task_folder, tex_file_path])
#     subprocess.run(["pdflatex", "-output-directory", task_folder, tex_ans_file_path])
#
#     # Удаление временных файлов после компиляции
#     for ext in [".tex", ".aux", ".log", ".out"]:
#         for filename in [tex_file_path, tex_ans_file_path]:
#             temp_file = f"{filename[:-4]}{ext}"
#             if os.path.exists(temp_file):
#                 os.remove(temp_file)
#
#     pdf_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations.pdf")
#     pdf_ans_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations_answer.pdf")
#
#     # Проверим, существуют ли PDF файлы
#     if not os.path.exists(pdf_file_path):
#         print(f"PDF файл {pdf_file_path} не был создан.")
#     if not os.path.exists(pdf_ans_file_path):
#         print(f"PDF файл {pdf_ans_file_path} не был создан.")


def generate_tex(task_info, count_of_task, count_of_eq):
    latex_code_for_all_task = (
            r'\documentclass[a4paper,12pt]{article}' + '\n'
                                                       r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
                                                                                                  r'\usepackage[T1,T2A]{fontenc}' + '\n'
                                                                                                                                    r'\usepackage[utf8]{inputenc}' + '\n'
                                                                                                                                                                     r'\usepackage[english, russian]{babel}' + '\n'
                                                                                                                                                                                                               r'\begin{document}' + '\n'
    )
    latex_code_for_all_answers = latex_code_for_all_task
    latex_code_for_all_answers += (
            r'\begin{center}' + '\n'
                                r'Ответы' + '\n'
                                            r'\end{center}' + '\n'
                                                              '\n'
    )

    group = task_info[3]
    cnt_of_students = 0

    groups = group.split(", ")

    all_task_latex = ""  # для общего файла с заданиями
    all_answer_latex = ""  # для общего файла с ответами
    student_task_latex = {}  # для заданий, сгруппированных по студентам
    student_answer_latex = {}  # для ответов, сгруппированных по студентам

    # Подготовка для каждого студента
    for group_of_students in groups:
        students = get_students_by_group(
            int(group_of_students))  # получаем студентов из группы в алфавитном порядке
        cnt_of_students += len(students)

        # Для студентов
        for student in students:
            student_name = student["full_name"]
            name_of_variant = (
                    r'\begin{center}' + '\n'
                                        rf'\textbf{{Вариант --- {student_name}}}' + '\n'
                                                                                    r'\end{center}' + '\n'
                                                                                                      '\n'
            )

            # Добавляем задания для общего файла и для конкретного студента
            all_task_latex += r'\newpage' + name_of_variant  # Каждое задание на новой странице
            all_answer_latex += r'\newpage' + name_of_variant
            student_task_latex[student_name] = name_of_variant
            student_answer_latex[student_name] = name_of_variant

            task_latex, ans_latex = generate_eq_for_variant(count_of_task, count_of_eq)

            all_task_latex += task_latex
            all_answer_latex += ans_latex
            student_task_latex[student_name] += task_latex
            student_answer_latex[student_name] += ans_latex

    latex_code_for_all_task += all_task_latex
    latex_code_for_all_answers += all_answer_latex

    latex_code_for_all_task += r'\end{document}' + '\n'
    latex_code_for_all_answers += r'\end{document}' + '\n'

    return latex_code_for_all_task, latex_code_for_all_answers, student_task_latex, student_answer_latex


def generate_pdf(task_info, count_of_task, count_of_eq):
    task_name = task_info[1]
    task_folder = os.path.join("task", task_name)

    if not os.path.exists(task_folder):
        os.makedirs(task_folder)

    latex_code, latex_code_for_ans, student_task_latex, student_answer_latex = generate_tex(task_info, count_of_task,
                                                                                            count_of_eq)

    tex_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations.tex")
    tex_ans_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations_answer.tex")

    with open(tex_file_path, "w") as file:
        file.write(latex_code)

    with open(tex_ans_file_path, "w") as file:
        file.write(latex_code_for_ans)

    # Компиляция общего PDF для всех заданий
    subprocess.run(["pdflatex", tex_file_path])
    subprocess.run(["pdflatex", tex_ans_file_path])

    # Генерация и перемещение файлов для каждого студента
    for student_name, student_tex_content in student_task_latex.items():
        # Преамбула для каждого студента
        student_latex_code = (
                r'\documentclass[a4paper,12pt]{article}' + '\n'
                                                           r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
                                                                                                      r'\usepackage[T1,T2A]{fontenc}' + '\n'
                                                                                                                                        r'\usepackage[utf8]{inputenc}' + '\n'
                                                                                                                                                                         r'\usepackage[english, russian]{babel}' + '\n'
                                                                                                                                                                                                                   r'\begin{document}' + '\n'
        )

        # Добавляем задания для студента
        student_latex_code += student_tex_content
        student_latex_code += r'\end{document}' + '\n'

        student_tex_file = os.path.join(task_folder, f"{task_name}_{student_name}.tex")
        with open(student_tex_file, "w") as f:
            f.write(student_latex_code)

        subprocess.run(["pdflatex", student_tex_file])

    # Генерация PDF для групповых ответов
    for group, group_answer in student_answer_latex.items():
        group_tex_file = os.path.join(task_folder, f"{task_name}_ans_for_group_{group}.tex")

        # Преамбула для групповых ответов
        group_latex_code = (
                r'\documentclass[a4paper,12pt]{article}' + '\n'
                                                           r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
                                                                                                      r'\usepackage[T1,T2A]{fontenc}' + '\n'
                                                                                                                                        r'\usepackage[utf8]{inputenc}' + '\n'
                                                                                                                                                                         r'\usepackage[english, russian]{babel}' + '\n'
                                                                                                                                                                                                                   r'\begin{document}' + '\n'
        )

        group_latex_code += group_answer
        group_latex_code += r'\end{document}' + '\n'

        with open(group_tex_file, "w") as f:
            f.write(group_latex_code)

        subprocess.run(["pdflatex", group_tex_file])

    # Удаление временных файлов после компиляции
    os.remove(tex_file_path)
    os.remove(f"{tex_file_path[:-4]}.aux")
    os.remove(f"{tex_file_path[:-4]}.log")
    os.remove(tex_ans_file_path)
    os.remove(f"{tex_ans_file_path[:-4]}.aux")
    os.remove(f"{tex_ans_file_path[:-4]}.log")
