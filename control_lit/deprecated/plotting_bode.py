"""Funções de plotagem Bode/Nyquist movidas para deprecated.

Mantidas aqui para referência histórica e testes.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from math import atan2, degrees, log10


def plot_bode(omega, magnitude_db, phase_deg):
    fig, (ax_mag, ax_phase) = plt.subplots(2, 1, figsize=(8.5, 7.5), sharex=True)
    ax_mag.semilogx(omega, magnitude_db, color="tab:blue", linewidth=2.0)
    ax_mag.set_ylabel("Magnitude (dB)")
    ax_mag.set_title("Diagrama de Bode")
    ax_mag.grid(True, which="both", alpha=0.3)

    ax_phase.semilogx(omega, phase_deg, color="tab:orange", linewidth=2.0)
    ax_phase.set_xlabel("Frequência angular (rad/s)")
    ax_phase.set_ylabel("Fase (graus)")
    ax_phase.grid(True, which="both", alpha=0.3)

    fig.tight_layout()
    return fig, (ax_mag, ax_phase)


def plot_nyquist(points):
    fig, ax = plt.subplots(figsize=(7, 7))
    real = [value.real for value in points]
    imag = [value.imag for value in points]
    ax.plot(real, imag, color="tab:purple", linewidth=2.0)
    if real and imag:
        ax.scatter([real[0]], [imag[0]], color="tab:green", label="Início")
        ax.scatter([real[-1]], [imag[-1]], color="tab:red", label="Fim")
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_title("Diagrama de Nyquist")
    ax.set_xlabel("Parte Real")
    ax.set_ylabel("Parte Imaginária")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig, ax
