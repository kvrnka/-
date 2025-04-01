import pytest
import sympy as sp
import numpy as np
import sys
import os
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator import generate_eq_for_variant, gaussian, generate_one_eq  # Импортируй свою реализацию


# 1. Тест генерации уравнений
def test_generate_one_eq():
    for _ in range(7):
        size = random.randint(1, 10)  # Размер матрицы от 1 до 10
        eq, a, b, x = generate_one_eq(size)  # Генерируем систему

        a_np = np.array(a.tolist(), dtype=float)
        b_np = np.array(b.tolist(), dtype=float)

        ans = np.linalg.solve(a_np, b_np)  # Решаем систему
        x_np = np.array(x, dtype=float)  # Преобразуем ответ в numpy-массив

        # Проверяем, совпадает ли решение (с небольшой погрешностью)
        assert np.allclose(ans.ravel(), x_np), f"Решение не совпало!\nОжидалось: {x_np}\nПолучено: {ans.ravel()}"


# 1. Тест на создание теха
def test_generate_eq_for_variant():
    count_of_task = 1
    count_of_eq = [3]  # 3 уравнения

    task_latex, ans_latex, solution_latex = generate_eq_for_variant(count_of_task, count_of_eq)

    assert "\\begin{cases}" in task_latex, "Latex-код не содержит систему уравнений!"
    assert ans_latex.strip() != "", "Ответы не сгенерировались!"
    assert solution_latex.strip() != "", "Решения не сгенерировались"


# 3. Тест метода Гаусса
def test_gaussian():
    A = sp.Matrix([[2, -1, 1], [1, 3, 2], [1, -1, 2]])
    B = sp.Matrix([8, 13, 7])

    solution_latex = gaussian(A, B)

    A_np = np.array(A.tolist(), dtype = float)
    B_np = np.array(B.tolist(), dtype = float)
    expected_solution = np.linalg.solve(A_np, B_np)  # Проверяем правильность

    assert "\\begin{cases}" not in solution_latex, "Latex-код не должен содержать систему!"
    assert expected_solution is not None, "Метод Гаусса не нашел решение!"


if __name__ == "__main__":
    pytest.main()
