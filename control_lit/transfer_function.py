"""Função de transferência em tempo contínuo para sistemas LIT.
Foi meio chato criar essa parte, mas é uma das mais importantes, porque é a base de tudo. Ela é a representação simbólica do sistema, e a partir dela a gente consegue calcular tudo o mais, como resposta ao impulso, resposta ao degrau, resposta a entradas arbitrárias, análise de estabilidade, análise de frequência, lugar das raízes, etc. Então eu fiz ela bem completa, com operações de soma, subtração, multiplicação, divisão e realimentação. Também tem a conversão para espaço de estados na forma canônica controlável, que é usada para simular a resposta temporal. E tem as propriedades para calcular polos e zeros usando as funções de raízes polinomiais da math_utils. Enfim, é a base de todo o processo de análise e simulação dos sistemas LIT."""

from __future__ import annotations

from dataclasses import dataclass

from .math_utils import (
    add_polynomials,
    convolve,
    normalize_polynomial,
    polynomial_roots,
    subtract_polynomials,
    trim_polynomial,
)


@dataclass(frozen=True)
class TransferFunction:
    """Representa G(s) = numerador(s) / denominador(s)."""

    numerator: list
    denominator: list

    def __post_init__(self):
        num = trim_polynomial(self.numerator)
        den = trim_polynomial(self.denominator)
        if den == [0.0]:
            raise ValueError("O denominador não pode ser nulo.")

        lead = den[0]
        object.__setattr__(self, "numerator", [value / lead for value in num])
        object.__setattr__(self, "denominator", [value / lead for value in den])

    def __add__(self, other):
        if not isinstance(other, TransferFunction):
            return NotImplemented
        numerator = add_polynomials(
            convolve(self.numerator, other.denominator),
            convolve(other.numerator, self.denominator),
        )
        denominator = convolve(self.denominator, other.denominator)
        return TransferFunction(numerator, denominator)

    def __sub__(self, other):
        if not isinstance(other, TransferFunction):
            return NotImplemented
        numerator = subtract_polynomials(
            convolve(self.numerator, other.denominator),
            convolve(other.numerator, self.denominator),
        )
        denominator = convolve(self.denominator, other.denominator)
        return TransferFunction(numerator, denominator)

    def __mul__(self, other):
        if not isinstance(other, TransferFunction):
            return NotImplemented
        return TransferFunction(
            convolve(self.numerator, other.numerator),
            convolve(self.denominator, other.denominator),
        )

    def __truediv__(self, other):
        if not isinstance(other, TransferFunction):
            return NotImplemented
        return TransferFunction(
            convolve(self.numerator, other.denominator),
            convolve(self.denominator, other.numerator),
        )

    @property
    def zeros(self):
        return polynomial_roots(self.numerator)

    @property
    def poles(self):
        return polynomial_roots(self.denominator)

    def feedback(self, other=None, sign=-1):
        """Fecha a malha com H(s). Padrão: realimentação unitária negativa."""

        other = other or TransferFunction([1.0], [1.0])
        loop = self * other
        if sign not in (-1, 1):
            raise ValueError("sign deve ser -1 para negativa ou 1 para positiva.")

        if sign == -1:
            denominator = add_polynomials(loop.denominator, loop.numerator)
        else:
            denominator = subtract_polynomials(loop.denominator, loop.numerator)

        numerator = convolve(self.numerator, other.denominator)
        return TransferFunction(numerator, denominator)

    def to_state_space(self):
        """Converte a função de transferência para forma canônica controlável.

        Retorna (A, B, C, D) como listas puras de Python.
        """

        num = trim_polynomial(self.numerator)
        den = normalize_polynomial(self.denominator)

        if den == [0.0]:
            raise ValueError("Denominador inválido.")

        order = len(den) - 1
        if order < 1:
            raise ValueError("A ordem do sistema deve ser pelo menos 1.")

        num = [value / self.denominator[0] for value in num]

        if len(num) < order + 1:
            num = [0.0] * (order + 1 - len(num)) + num
        elif len(num) > order + 1:
            raise ValueError("O sistema deve ser próprio ou estritamente próprio.")

        a = den[1:]
        b = num
        d = b[0]
        c_coeffs = [b[order - i] - a[order - i - 1] * d for i in range(order)]

        A = [[0.0 for _ in range(order)] for _ in range(order)]
        for i in range(order - 1):
            A[i][i + 1] = 1.0
        A[-1] = [-value for value in reversed(a)]

        B = [[0.0] for _ in range(order)]
        B[-1][0] = 1.0

        C = [c_coeffs]
        D = [[d]]
        return A, B, C, D