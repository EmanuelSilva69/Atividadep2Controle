"""Análise em frequência para diagramas de Bode e Nyquist.

(Arquivo movido para `deprecated/` — mantido para referência histórica.)
"""

from __future__ import annotations

from math import atan2, degrees, log10

from ..math_utils import polyval
from ..transfer_function import TransferFunction


def _evaluate_tf_at_frequency(tf, omega):
    s = complex(0.0, omega)
    numerator = polyval(tf.numerator, s)
    denominator = polyval(tf.denominator, s)
    return numerator / denominator


def frequency_response(tf, omega_values):
    """Retorna a resposta complexa G(jw) para uma lista de frequências."""

    if not isinstance(tf, TransferFunction):
        raise TypeError("tf deve ser uma instância de TransferFunction.")

    values = []
    for omega in omega_values:
        values.append(_evaluate_tf_at_frequency(tf, omega))
    return values


def bode_data(tf, omega_values):
    """Calcula magnitude em dB e fase em graus para o diagrama de Bode."""

    response = frequency_response(tf, omega_values)
    magnitude_db = []
    phase_deg = []
    for value in response:
        magnitude = abs(value)
        magnitude_db.append(20.0 * log10(magnitude) if magnitude > 0 else float("-inf"))
        phase_deg.append(degrees(atan2(value.imag, value.real)))
    return magnitude_db, phase_deg


def nyquist_data(tf, omega_values):
    """Retorna a curva de Nyquist com simetria para frequências negativas."""

    positive = frequency_response(tf, omega_values)
    mirrored = [complex(value.real, -value.imag) for value in reversed(positive[1:])]
    return positive + mirrored
