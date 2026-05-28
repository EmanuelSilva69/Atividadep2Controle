"""Utilitários matemáticos puros para polinômios e álgebra numérica.
é a base matemática de todo o processo. Usei só math. Não tem problema né
Os coeficientes são representados em ordem decrescente de grau.
Exemplo: s^2 + 2s + 1 -> [1, 2, 1].
"""

from __future__ import annotations

import cmath
from math import isclose, pi


def trim_polynomial(coefficients, tol=1e-12):
    """Remove zeros à esquerda e normaliza pequenos resíduos numéricos."""

    if not coefficients:
        return [0.0]

    cleaned = [0.0 if abs(value) < tol else value for value in coefficients]
    index = 0
    while index < len(cleaned) - 1 and abs(cleaned[index]) < tol:
        index += 1
    result = cleaned[index:]
    return result if result else [0.0]


def normalize_polynomial(coefficients, tol=1e-12):
    """Remove zeros à esquerda e força o coeficiente líder igual a 1."""

    cleaned = trim_polynomial(coefficients, tol=tol)
    lead = cleaned[0]
    if isclose(abs(lead), 0.0, abs_tol=tol):
        return [0.0]
    return [value / lead for value in cleaned]


def _align_left(a, b):
    size = max(len(a), len(b))
    left = [0.0] * (size - len(a)) + list(a)
    right = [0.0] * (size - len(b)) + list(b)
    return left, right


def add_polynomials(a, b):
    """Soma dois polinômios alinhando os coeficientes por grau."""

    left, right = _align_left(a, b)
    return trim_polynomial([x + y for x, y in zip(left, right)])


def subtract_polynomials(a, b):
    """Subtrai b de a."""

    left, right = _align_left(a, b)
    return trim_polynomial([x - y for x, y in zip(left, right)])


def convolve(a, b):
    """Multiplicação de polinômios em ordem decrescente de grau."""

    if not a or not b:
        return [0.0]

    result = [0.0] * (len(a) + len(b) - 1)
    for i, coef_a in enumerate(a):
        for j, coef_b in enumerate(b):
            result[i + j] += coef_a * coef_b
    return trim_polynomial(result)


def polynomial_derivative(coefficients):
    """Retorna a derivada formal do polinômio."""

    coefficients = trim_polynomial(coefficients)
    degree = len(coefficients) - 1
    if degree <= 0:
        return [0.0]

    derivative = []
    for index, coef in enumerate(coefficients[:-1]):
        power = degree - index
        derivative.append(coef * power)
    return trim_polynomial(derivative)


def polyval(coefficients, x):
    """Avalia um polinômio em x usando o esquema de Horner."""

    result = 0
    for coef in coefficients:
        result = result * x + coef
    return result


def polynomial_scale(coefficients, scalar):
    """Multiplica todos os coeficientes por um escalar."""

    return trim_polynomial([scalar * value for value in coefficients])


def polynomial_to_string(coefficients, variable="s"):
    """Formata um polinômio para exibição legível."""

    coefficients = trim_polynomial(coefficients)
    degree = len(coefficients) - 1
    if degree < 0:
        return "0"

    terms = []
    for index, coef in enumerate(coefficients):
        power = degree - index
        if abs(coef) < 1e-12:
            continue

        sign = "-" if coef < 0 else "+"
        magnitude = abs(coef)
        if power == 0:
            core = f"{magnitude:g}"
        elif power == 1:
            core = f"{magnitude:g}{variable}"
        else:
            core = f"{magnitude:g}{variable}^{power}"

        if not terms:
            terms.append(core if coef >= 0 else f"-{core}")
        else:
            terms.append(f" {sign} {core}")

    return "".join(terms) if terms else "0"


def _initial_root_guesses(degree):
    radius = 1.0
    if degree <= 0:
        return []

    guesses = []
    for k in range(degree):
        angle = 2.0 * pi * k / degree
        guesses.append(radius * cmath.exp(1j * angle))
    return guesses


def polynomial_roots(coefficients, max_iter=200, tol=1e-12):
    """Encontra raízes complexas usando o método de Durand-Kerner.

    O algoritmo é robusto o suficiente para as necessidades deste projeto,
    inclusive para raízes complexas conjugadas e multiplicidades baixas.
    """

    polynomial = trim_polynomial(coefficients, tol=tol)
    degree = len(polynomial) - 1
    if degree < 1:
        return []
    if degree == 1:
        return [-polynomial[1] / polynomial[0]]

    monic = normalize_polynomial(polynomial, tol=tol)
    roots = _initial_root_guesses(degree)
    if not roots:
        return []

    for _ in range(max_iter):
        max_delta = 0.0
        new_roots = roots[:]
        for i in range(degree):
            denominator = 1 + 0j
            for j in range(degree):
                if i != j:
                    diff = roots[i] - roots[j]
                    if abs(diff) < tol:
                        diff = tol + 0j
                    denominator *= diff

            value = polyval(monic, roots[i])
            delta = value / denominator
            new_roots[i] = roots[i] - delta
            max_delta = max(max_delta, abs(delta))

        roots = new_roots
        if max_delta < tol:
            break

    return roots