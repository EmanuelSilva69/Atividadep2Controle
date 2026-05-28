"""Cálculo do lugar das raízes em Python puro."""

from __future__ import annotations

from .math_utils import add_polynomials, polynomial_roots
from .transfer_function import TransferFunction


def root_locus(tf, gains):
    """Calcula as raízes da equação característica para cada ganho K.

    Retorna uma lista de dicionários com chaves:
    - K: ganho considerado
    - roots: raízes de malha fechada
    - poles: polos de malha aberta
    - zeros: zeros de malha aberta
    é a base de cácluclo dos polos e zeros. basicamente continua da math Utils e usa o que está presente lá para o calculo real!!!
    """

    if not isinstance(tf, TransferFunction):
        raise TypeError("tf deve ser uma instância de TransferFunction.")

    roots_data = []
    open_loop_poles = tf.poles
    open_loop_zeros = tf.zeros

    den = tf.denominator
    num = tf.numerator

    for gain in gains:
        characteristic = add_polynomials(den, [gain * value for value in num])
        roots = polynomial_roots(characteristic)
        roots_data.append(
            {
                "K": gain,
                "roots": roots,
                "poles": open_loop_poles,
                "zeros": open_loop_zeros,
            }
        )

    return roots_data