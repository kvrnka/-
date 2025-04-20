import random
import sympy as sp
import subprocess
import os
from databases_methods.list_of_students_methods import get_students_by_group, get_unique_group_numbers


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


def gaussian(a_matrix, b_matrix):
    n = a_matrix.shape[0]
    aug_matrix = a_matrix.row_join(b_matrix)  # Расширенная матрица A|B
    latex_code = r'Составим расширенную матрицу:' + '\n\n'
    latex_code += r'\[' + sp.latex(aug_matrix) + r'\]' + '\n\n'
    latex_code += r'Приведём матрицу к верхнетреугольному виду:' + '\n\n'

    # приводим к верхнетреугольному виду
    for col in range(n):
        latex_code += rf'{col + 1}.'
        pivot_row = col  # строка с ведущим элементом
        pivot = aug_matrix[pivot_row, col]  # диагональный элемент
        if pivot == 0:
            for row in range(col + 1, n):
                if aug_matrix[row, col] != 0:
                    aug_matrix.row_swap(pivot_row, row)
                    latex_code += rf'Меняем местами {col + 1} и {row + 1} строки:' + '\n\n'
                    latex_code += r'\[' + sp.latex(aug_matrix) + r'\]' + '\n\n'
                    pivot = aug_matrix[pivot_row, col]
                    break

        if pivot != 0:
            aug_matrix[pivot_row, :] /= pivot  # Приведение ведущего элемента к 1
            latex_code += rf'Делим {pivot_row + 1} строку на {pivot}:' + '\n\n'
            latex_code += r'\[' + sp.latex(aug_matrix) + r'\]' + '\n\n'

        for row in range(col + 1, n):
            factor = aug_matrix[row, col]
            aug_matrix[row, :] -= factor * aug_matrix[pivot_row, :]
        latex_code += rf'Обнуляем элементы ниже ведущего:' + '\n\n'
        latex_code += r'\[' + sp.latex(aug_matrix) + r'\]' + '\n\n'

    latex_code += r'Приведём матрицу к улучшенному ступенчатому виду:' + '\n\n'

    for col in range(n - 1, -1, -1):
        for row in range(col):
            factor = aug_matrix[row, col]
            aug_matrix[row, :] -= factor * aug_matrix[col, :]
        latex_code += rf'Обнулим элементы выше ведущего элемента {col + 1} строки:' + '\n\n'
        latex_code += r'\[' + sp.latex(aug_matrix) + r'\]' + '\n\n'
    return latex_code


# функция для определения пропорциональности строк, чтобы не допускать обнуления строки
# def is_proportional(ai, row):
#     relation = 0
#     for ai_elem, row_elem in zip(ai, row):
#         if ai_elem == 0 and row_elem == 0:
#             continue
#         elif ai_elem == 0 and row_elem != 0 or ai_elem != 0 and row_elem == 0:
#             return False
#         else:
#             ratio = ai_elem / row_elem
#             if relation == 0:
#                 relation = ratio
#             elif relation != ratio:
#                 return False
#     return True


def generate_one_eq(count_of_eq):
    x_ans = [random.randint(-15, 15) for _ in range(count_of_eq)]  # генерируем ответ
    while x_ans == [0] * count_of_eq:
        x_ans = [random.randint(-10, 10) for _ in range(count_of_eq)]

    # Генерация невырожденной матрицы A
    while True:
        a_matrix = sp.Matrix([[random.randint(-10, 10) for _ in range(count_of_eq)] for _ in range(count_of_eq)])
        if a_matrix.det() != 0:
            break  # Матрица невырожденная

    x_vector = sp.Matrix(x_ans)
    b_vector = a_matrix * x_vector

    x_i = sp.symbols(f'x1:{count_of_eq + 1}')
    x_vector = sp.Matrix(x_i)
    equations = [sp.Eq(lhs, rhs) for lhs, rhs in zip(a_matrix * x_vector, b_vector)]
    return equations, a_matrix, b_vector, x_ans  # система, матрица коэффициентов, вектор b, ответ


# функция для генерации заданий для одного варианта
def generate_eq_for_variant(count_of_task, count_of_eq):
    latex_code_one_variants = ''
    latex_code_ans = ''
    latex_code_solution = ''
    for task in range(count_of_task):
        equations, a_matrix, b_vector, x_ans = generate_one_eq(count_of_eq[task])

        task_tex = from_equations_to_latex(equations)
        # сохранили условие
        latex_code_one_variants += rf'Задание {task + 1}.\\' + '\n\n'
        latex_code_one_variants += task_tex + '\n'
        # сохранили условие в файл с решениями
        latex_code_solution += rf'Задание {task + 1}.\\' + '\n\n'
        latex_code_solution += task_tex + '\n\n'

        solution = gaussian(a_matrix, b_vector)
        # добавляем тех решения
        latex_code_solution += solution

        vector_string = r'$ ('

        for elem in x_ans:
            vector_string += rf'{elem},'

        vector_string = vector_string[:-1] + r') $'

        latex_code_ans += (
                rf'{task + 1}.' + '\n'
                + vector_string + '\n'
        )
        latex_code_solution += (
                rf'Ответ:' + '\n'
                + vector_string + '\n\n'
        )

    return latex_code_one_variants, latex_code_ans, latex_code_solution


def generate_tex(task_info, count_of_task, count_of_eq):
    preambula = r'\documentclass[a4paper,12pt]{article}' + '\n'
    preambula += r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
    preambula += r'\usepackage[T1,T2A]{fontenc}' + '\n'
    preambula += r'\usepackage[utf8]{inputenc}' + '\n'
    preambula += r'\usepackage[english, russian]{babel}' + '\n'
    preambula += r'\begin{document}' + '\n'
    latex_code_for_all_task = preambula
    latex_code_for_all_answers = preambula
    latex_code_for_all_answers += (
            r'\begin{center}' + '\n'
                                r'Ответы' + '\n'
                                            r'\end{center}' + '\n'
                                                              '\n'
    )

    end_doc = r'\end{document}' + '\n'

    group = task_info[3]

    if group.lower() == 'все':
        groups = get_unique_group_numbers()
    else:
        groups = [groups_.strip() for groups_ in group.split(',')]
        # groups = group.split(", ")
        groups = sorted(groups)

    all_task_latex = ""  # для общего файла с заданиями
    all_answer_latex = ""  # для общего файла с ответами
    all_solution_latex = preambula  # для общего файла с решениями
    student_task_latex = {}  # для заданий, сгруппированных по студентам
    group_answer_latex = {}  # для ответов, сгруппированных по группам
    group_condition_latex = {}  # ответы для определенной группы в одном файле
    group_solution_latex = {}  # решения для определенной группы в одном файле

    # Подготовка для каждого студента
    for group_of_students in groups:
        students = get_students_by_group(
            int(group_of_students))  # получаем студентов из группы в алфавитном порядке

        name_for_ans = r'\begin{center}' + '\n'
        name_for_ans += rf'\textbf{{Группа - {group_of_students}}}' + '\n'
        name_for_ans += r'\end{center}' + '\n' + '\n'

        all_answer_latex += name_for_ans

        ans_for_current_group = preambula + name_for_ans
        condition_for_current_group = preambula + name_for_ans
        solution_for_current_group = preambula + name_for_ans

        for student in students:
            student_name = student["full_name"]
            name_of_variant = r'\begin{center}' + '\n'
            name_of_variant += rf'\textbf{{Вариант - {student_name}, группа {group_of_students}}}' + '\n'
            name_of_variant += r'\end{center}' + '\n' + '\n'

            key_for_student = f"{student_name}_{group_of_students}"
            # Добавляем задания для общего файла и для конкретного студента
            all_task_latex += name_of_variant
            all_answer_latex += name_of_variant
            all_solution_latex += name_of_variant
            condition_for_current_group += name_of_variant
            solution_for_current_group += name_of_variant
            student_task_latex[key_for_student] = preambula + name_of_variant
            ans_for_current_group += name_of_variant

            task_latex, ans_latex, solution_latex = generate_eq_for_variant(count_of_task, count_of_eq)

            all_task_latex += task_latex + r'\newpage'
            all_answer_latex += ans_latex
            all_solution_latex += solution_latex + r'\newpage'
            condition_for_current_group += task_latex + r'\newpage'
            solution_for_current_group += solution_latex + r'\newpage'
            student_task_latex[key_for_student] += task_latex + end_doc
            ans_for_current_group += ans_latex
        group_answer_latex[group_of_students] = ans_for_current_group + end_doc
        group_condition_latex[group_of_students] = condition_for_current_group + end_doc
        group_solution_latex[group_of_students] = solution_for_current_group + end_doc

    latex_code_for_all_task += all_task_latex
    latex_code_for_all_answers += all_answer_latex + r'\newpage'

    all_solution_latex += end_doc + '\n'
    latex_code_for_all_task += r'\end{document}' + '\n'
    latex_code_for_all_answers += r'\end{document}' + '\n'

    return (latex_code_for_all_task, latex_code_for_all_answers, student_task_latex,
            group_answer_latex, group_condition_latex, all_solution_latex, group_solution_latex)


def generate_pdf(task_info, count_of_task, count_of_eq):
    task_name = task_info[1]
    task_folder = os.path.join("task", task_name)

    if not os.path.exists(task_folder):
        os.makedirs(task_folder)

    (latex_code, latex_code_for_ans, student_task_latex, student_answer_latex, group_condition_latex,
     all_solution_latex, group_solution_latex) = generate_tex(task_info, count_of_task, count_of_eq)

    tex_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations.tex")
    tex_ans_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations_answer.tex")
    tex_solution_file_path = os.path.join(task_folder, f"{task_name}_system_of_equations_solution.tex")

    with open(tex_file_path, "w") as file:
        file.write(latex_code)

    with open(tex_ans_file_path, "w") as file:
        file.write(latex_code_for_ans)

    with open(tex_solution_file_path, "w") as file:
        file.write(all_solution_latex)

    # Компиляция общего PDF для всех заданий
    subprocess.run(["pdflatex", "-output-directory", task_folder, tex_file_path])
    subprocess.run(["pdflatex", "-output-directory", task_folder, tex_ans_file_path])
    subprocess.run(["pdflatex", "-output-directory", task_folder, tex_solution_file_path])

    for student_name, student_tex_content in student_task_latex.items():
        student_latex_code = student_tex_content
        student_tex_file = os.path.join(task_folder, f"{task_name}_{student_name}.tex")
        with open(student_tex_file, "w") as f:
            f.write(student_latex_code)
        subprocess.run(["pdflatex", "-output-directory", task_folder, student_tex_file])

    for group, group_answer in student_answer_latex.items():
        group_tex_file = os.path.join(task_folder, f"{task_name}_ans_for_group_{group}.tex")
        group_latex_code = group_answer
        with open(group_tex_file, "w") as f:
            f.write(group_latex_code)
        subprocess.run(["pdflatex", "-output-directory", task_folder, group_tex_file])

    for group, group_condition in group_condition_latex.items():
        group_tex_file = os.path.join(task_folder, f"{task_name}_condition_for_group_{group}.tex")
        group_latex_code = group_condition
        with open(group_tex_file, "w") as f:
            f.write(group_latex_code)
        subprocess.run(["pdflatex", "-output-directory", task_folder, group_tex_file])

    for group, group_solution in group_solution_latex.items():
        print("i'm here")
        group_tex_file = os.path.join(task_folder, f"{task_name}_solution_for_group_{group}.tex")
        group_latex_code = group_solution
        with open(group_tex_file, "w") as f:
            f.write(group_latex_code)
        subprocess.run(["pdflatex", "-output-directory", task_folder, group_tex_file])

    # Удаление временных файлов после компиляции
    for file in os.listdir(task_folder):
        if file.endswith((".aux", ".tex", ".log")):
            file_path = os.path.join(task_folder, file)  # Создаём полный путь
            os.remove(file_path)
