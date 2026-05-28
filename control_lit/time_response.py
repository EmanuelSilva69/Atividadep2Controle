"""Simulação temporal via integração numérica em Python puro."""

from __future__ import annotations

from .transfer_function import TransferFunction


def _mat_vec_mul(matrix, vector):
    return [sum(row[j] * vector[j] for j in range(len(vector))) for row in matrix]


def _vec_add(a, b):
    return [x + y for x, y in zip(a, b)]


def _vec_scale(vector, scalar):
    return [scalar * value for value in vector]


def _rk4_step(A, B, C, D, state, input_value, dt):
    def f(current_state):
        Ax = _mat_vec_mul(A, current_state)
        Bu = [row[0] * input_value for row in B]
        return _vec_add(Ax, Bu)

    k1 = f(state)
    k2 = f(_vec_add(state, _vec_scale(k1, dt / 2.0)))
    k3 = f(_vec_add(state, _vec_scale(k2, dt / 2.0)))
    k4 = f(_vec_add(state, _vec_scale(k3, dt)))

    increment = _vec_scale(
        _vec_add(
            _vec_add(k1, _vec_scale(_vec_add(k2, k3), 2.0)),
            k4,
        ),
        dt / 6.0,
    )
    next_state = _vec_add(state, increment)

    y = sum(C[0][i] * next_state[i] for i in range(len(next_state))) + D[0][0] * input_value
    return next_state, y


def _simulate(tf, t_max, dt, input_function):
    if not isinstance(tf, TransferFunction):
        raise TypeError("tf deve ser uma instância de TransferFunction.")
    if t_max <= 0 or dt <= 0:
        raise ValueError("t_max e dt devem ser positivos.")

    A, B, C, D = tf.to_state_space()
    order = len(A)
    state = [0.0] * order
    t_values = []
    y_values = []

    steps = int(round(t_max / dt))
    for step in range(steps + 1):
        current_time = step * dt
        u = input_function(current_time, step)
        t_values.append(current_time)
        if step == 0:
            y = sum(C[0][i] * state[i] for i in range(order)) + D[0][0] * u
            y_values.append(y)
        else:
            state, y = _rk4_step(A, B, C, D, state, u, dt)
            y_values.append(y)

    return t_values, y_values


def step_response(tf, t_max, dt):
    """Resposta ao degrau unitário."""

    return _simulate(tf, t_max, dt, lambda _t, _k: 1.0)


def impulse_response(tf, t_max, dt):
    """Resposta ao impulso aproximada por uma amostragem discreta de área 1."""

    amplitude = 1.0 / dt

    def impulse(_t, step):
        return amplitude if step == 0 else 0.0

    return _simulate(tf, t_max, dt, impulse)