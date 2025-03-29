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


# добавить обработку, когда для всех
def generate_tex(task_info, count_of_task, count_of_eq):
    preambula = (
            r'\documentclass[a4paper,12pt]{article}' + '\n'
                                                       r'\usepackage{amsmath, amsthm, amssymb}' + '\n'
                                                                                                  r'\usepackage[T1,T2A]{fontenc}' + '\n'
                                                                                                                                    r'\usepackage[utf8]{inputenc}' + '\n'
                                                                                                                                                                     r'\usepackage[english, russian]{babel}' + '\n'
                                                                                                                                                                                                               r'\begin{document}' + '\n'
    )
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
    cnt_of_students = 0

    groups = group.split(", ")

    all_task_latex = ""  # для общего файла с заданиями
    all_answer_latex = ""  # для общего файла с ответами
    student_task_latex = {}  # для заданий, сгруппированных по студентам
    group_answer_latex = {}  # для ответов, сгруппированных по группам

    # Подготовка для каждого студента
    for group_of_students in groups:
        students = get_students_by_group(
            int(group_of_students))  # получаем студентов из группы в алфавитном порядке
        cnt_of_students += len(students)

        name_for_ans = (
                r'\begin{center}' + '\n'
                                    rf'\textbf{{Группа - {group_of_students}}}' + '\n'
                                                                                  r'\end{center}' + '\n'
                                                                                                    '\n'
        )

        all_answer_latex += name_for_ans

        ans_for_current_group = preambula + name_for_ans

        for student in students:
            student_name = student["full_name"]
            name_of_variant = (
                    r'\begin{center}' + '\n'
                                        rf'\textbf{{Вариант - {student_name}}}' + '\n'
                                                                                  r'\end{center}' + '\n'
                                                                                                    '\n'
            )

            # Добавляем задания для общего файла и для конкретного студента
            all_task_latex += name_of_variant
            all_answer_latex += name_of_variant
            student_task_latex[student_name] = preambula + name_of_variant
            ans_for_current_group += name_of_variant

            task_latex, ans_latex = generate_eq_for_variant(count_of_task, count_of_eq)

            all_task_latex += task_latex + r'\newpage'
            all_answer_latex += ans_latex
            student_task_latex[student_name] += task_latex + end_doc
            ans_for_current_group += ans_latex
        group_answer_latex[group_of_students] = ans_for_current_group + end_doc

    latex_code_for_all_task += all_task_latex
    latex_code_for_all_answers += all_answer_latex + r'\newpage'

    latex_code_for_all_task += r'\end{document}' + '\n'
    latex_code_for_all_answers += r'\end{document}' + '\n'

    return latex_code_for_all_task, latex_code_for_all_answers, student_task_latex, group_answer_latex


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
    subprocess.run(["pdflatex", "-output-directory", task_folder, tex_file_path])
    subprocess.run(["pdflatex", "-output-directory", task_folder, tex_ans_file_path])

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

    # Удаление временных файлов после компиляции
    for file in os.listdir(task_folder):
        if file.endswith((".aux", ".tex", ".log")):
            file_path = os.path.join(task_folder, file)  # Создаём полный путь
            os.remove(file_path)
