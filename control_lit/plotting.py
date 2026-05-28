"""Funções de visualização com Matplotlib."""

from __future__ import annotations

from math import acos, cos, sin

import matplotlib.pyplot as plt


def plot_pole_zero_map(zeros, poles):
    fig, ax = plt.subplots(figsize=(7, 7))

    zero_real = [value.real for value in zeros]
    zero_imag = [value.imag for value in zeros]
    pole_real = [value.real for value in poles]
    pole_imag = [value.imag for value in poles]

    if zeros:
        ax.scatter(
            zero_real,
            zero_imag,
            marker="o",
            s=90,
            facecolors="none",
            edgecolors="tab:green",
            linewidths=2.0,
            label="Zeros",
        )
    if poles:
        ax.scatter(
            pole_real,
            pole_imag,
            marker="x",
            s=90,
            color="tab:red",
            linewidths=2.0,
            label="Polos",
        )

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_title("Mapa de Polos e Zeros")
    ax.set_xlabel("Parte Real")
    ax.set_ylabel("Parte Imaginária")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig, ax


def plot_pole_zero_zoom(zeros, poles, center=0.0, span=4.0):
    fig, ax = plt.subplots(figsize=(7, 7))

    zero_real = [value.real for value in zeros]
    zero_imag = [value.imag for value in zeros]
    pole_real = [value.real for value in poles]
    pole_imag = [value.imag for value in poles]

    if zeros:
        ax.scatter(
            zero_real,
            zero_imag,
            marker="o",
            s=90,
            facecolors="none",
            edgecolors="tab:green",
            linewidths=2.0,
            label="Zeros",
        )
    if poles:
        ax.scatter(
            pole_real,
            pole_imag,
            marker="x",
            s=90,
            color="tab:red",
            linewidths=2.0,
            label="Polos",
        )

    center = complex(center)
    span = max(float(span), 1e-6)
    ax.scatter([center.real], [center.imag], marker="+", s=120, color="tab:blue", label="Centro")
    ax.axhline(center.imag, color="tab:blue", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.axvline(center.real, color="tab:blue", linewidth=0.8, linestyle="--", alpha=0.5)

    ax.set_xlim(center.real - span, center.real + span)
    ax.set_ylim(center.imag - span, center.imag + span)
    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_title("Zoom de Polos e Zeros")
    ax.set_xlabel("Parte Real")
    ax.set_ylabel("Parte Imaginária")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig, ax



def plot_step_response(t, y):
    return plot_time_response(t, y, title="Resposta ao Degrau")


def plot_time_response(t, y, title="Resposta no Tempo"):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(t, y, linewidth=2.0)
    ax.set_title(title)
    ax.set_xlabel("Tempo (s)")
    ax.set_ylabel("Amplitude")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig, ax


def plot_root_locus(roots_data):
    fig, ax = plt.subplots(figsize=(7, 7))

    plotted_poles = False
    plotted_zeros = False

    for entry in roots_data:
        roots = entry.get("roots", [])
        real = [root.real for root in roots]
        imag = [root.imag for root in roots]
        ax.plot(real, imag, marker=".", linestyle="none", color="tab:blue", alpha=0.75)

        if not plotted_poles:
            pole_values = entry.get("poles", [])
            zero_values = entry.get("zeros", [])
            if pole_values:
                ax.scatter(
                    [value.real for value in pole_values],
                    [value.imag for value in pole_values],
                    marker="x",
                    s=80,
                    color="tab:red",
                    label="Polos de malha aberta",
                )
                plotted_poles = True
            if zero_values:
                ax.scatter(
                    [value.real for value in zero_values],
                    [value.imag for value in zero_values],
                    marker="o",
                    s=70,
                    facecolors="none",
                    edgecolors="tab:green",
                    label="Zeros de malha aberta",
                )
                plotted_zeros = True

    ax.axhline(0.0, color="black", linewidth=0.8)
    ax.axvline(0.0, color="black", linewidth=0.8)
    ax.set_title("Lugar das Raízes")
    ax.set_xlabel("Parte Real")
    ax.set_ylabel("Parte Imaginária")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="best")
    fig.tight_layout()
    return fig, ax


def plot_root_locus_with_zeta(roots_data, zeta=None):
    fig, ax = plot_root_locus(roots_data)

    if zeta is not None:
        zeta = max(min(float(zeta), 0.999999), -0.999999)
        angle = acos(zeta)
        limit = max(
            1.0,
            abs(ax.get_xlim()[0]),
            abs(ax.get_xlim()[1]),
            abs(ax.get_ylim()[0]),
            abs(ax.get_ylim()[1]),
        )
        x_values = [-limit * cos(angle), 0.0]
        y_values = [limit * sin(angle), 0.0]
        ax.plot(x_values, y_values, linestyle="--", linewidth=1.6, color="tab:orange", label=f"ζ = {zeta:g}")
        ax.plot(x_values, [-value for value in y_values], linestyle="--", linewidth=1.6, color="tab:orange")
        ax.legend(loc="best")

    fig.tight_layout()
    return fig, ax