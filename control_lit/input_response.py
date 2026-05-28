"""Simulação de respostas para entradas arbitrárias em sistemas LIT."""

from __future__ import annotations

from .time_response import _rk4_step
from .transfer_function import TransferFunction


def arbitrary_input_response(tf, t_max, dt, input_signal):
    """Simula a resposta para uma entrada arbitrária.

    input_signal pode ser uma função u(t) ou uma lista de amostras.
    """

    if not isinstance(tf, TransferFunction):
        raise TypeError("tf deve ser uma instância de TransferFunction.")
    if t_max <= 0 or dt <= 0:
        raise ValueError("t_max e dt devem ser positivos.")

    A, B, C, D = tf.to_state_space()
    order = len(A)
    state = [0.0] * order
    t_values = []
    y_values = []

    if callable(input_signal):
        def get_input(time_value, step):
            return float(input_signal(time_value))
    else:
        samples = list(input_signal)

        def get_input(_time_value, step):
            return float(samples[step]) if step < len(samples) else 0.0

    steps = int(round(t_max / dt))
    for step in range(steps + 1):
        current_time = step * dt
        u = get_input(current_time, step)
        t_values.append(current_time)
        if step == 0:
            y = sum(C[0][i] * state[i] for i in range(order)) + D[0][0] * u
            y_values.append(y)
        else:
            state, y = _rk4_step(A, B, C, D, state, u, dt)
            y_values.append(y)

    return t_values, y_values