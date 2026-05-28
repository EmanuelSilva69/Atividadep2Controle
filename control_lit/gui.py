"""Interface gráfica para focar em polos, zeros e lugar das raízes, com extras opcionais."""

from __future__ import annotations

import ast
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

import matplotlib.pyplot as plt

from .analysis_explainer import explain_system
from .gif_tools import create_calculation_gif
from .input_response import arbitrary_input_response
from .plotting import plot_pole_zero_map, plot_pole_zero_zoom, plot_root_locus_with_zeta, plot_time_response
from .root_locus import root_locus
from .time_response import impulse_response, step_response
from .transfer_function import TransferFunction


class ControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LIT Studio")
        self.geometry("1180x760")
        self.minsize(1080, 700)
        self.configure(bg="#0f1720")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("TFrame", background="#0f1720")
        self.style.configure("Card.TFrame", background="#17212b", relief="flat")
        self.style.configure("TLabel", background="#0f1720", foreground="#e5eef7", font=("Segoe UI", 10))
        self.style.configure("Title.TLabel", background="#0f1720", foreground="#f8fafc", font=("Segoe UI Semibold", 20))
        self.style.configure("Accent.TButton", font=("Segoe UI Semibold", 10), padding=10)
        self.style.map("Accent.TButton", background=[("active", "#2563eb")])

        self.numerator_var = tk.StringVar(value="[1]")
        self.denominator_var = tk.StringVar(value="[1, 2, 1]")
        self.gains_var = tk.StringVar(value="[x * 0.2 for x in range(51)]")
        self.variable_var = tk.StringVar(value="s")
        self.zoom_center_var = tk.StringVar(value="0")
        self.zoom_span_var = tk.StringVar(value="4.0")
        self.zeta_var = tk.StringVar(value="0.5")
        self.dt_var = tk.StringVar(value="0.01")
        self.tmax_var = tk.StringVar(value="10.0")

        self._build_ui()

    def _build_ui(self):
        header = ttk.Frame(self, style="TFrame")
        header.pack(fill="x", padx=18, pady=(18, 12))
        ttk.Label(header, text="LIT Studio", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Análise de polos, zeros e lugar das raízes, com janela central e linha de ζ.").pack(anchor="w", pady=(4, 0))

        body = ttk.Frame(self, style="TFrame")
        body.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        left_container = ttk.Frame(body, style="Card.TFrame")
        left_container.pack(side="left", fill="y")

        left_canvas = tk.Canvas(left_container, borderwidth=0, background="#17212b", highlightthickness=0)
        left_scroll = ttk.Scrollbar(left_container, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scroll.set)

        left_inner = ttk.Frame(left_canvas, style="Card.TFrame", padding=18)
        left_canvas.create_window((0, 0), window=left_inner, anchor="nw")

        left_canvas.pack(side="left", fill="y", expand=True)
        left_scroll.pack(side="right", fill="y")

        def _on_frame_config(_event):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))

        left_inner.bind("<Configure>", _on_frame_config)
        right = ttk.Frame(body, style="Card.TFrame", padding=18)
        right.pack(side="right", fill="both", expand=True, padx=(18, 0))

        self._build_inputs(left_inner)
        self._build_output(right)

    def _build_inputs(self, parent):
        self._build_section(
            parent,
            title="Análise principal",
            subtitle="Aqui fica o fluxo central: polos, zeros e lugar das raízes.",
            fields=[
                ("Variável", self.variable_var),
                ("Numerador", self.numerator_var),
                ("Denominador", self.denominator_var),
                ("Ganhos K", self.gains_var),
                ("Centro do zoom", self.zoom_center_var),
                ("Janela do zoom", self.zoom_span_var),
                ("ζ", self.zeta_var),
            ],
            buttons=[
                ("Analisar sistema", self.analyze),
                ("Plotar polos e zeros", self.show_poles_zeros),
                ("Zoom polos/zeros", self.show_poles_zeros_zoom),
                ("Plotar Root Locus com ζ", self.show_root_locus),
            ],
            bottom_padding=18,
        )

        self._build_section(
            parent,
            title="Extras simples",
            subtitle="Respostas no tempo e exportação, sem análise pesada.",
            fields=[
                ("Δt", self.dt_var),
                ("Tmax", self.tmax_var),
            ],
            buttons=[
                ("Resposta ao degrau unitário", self.show_step),
                ("Resposta ao impulso", self.show_impulse),
                ("Resposta à rampa", self.show_ramp),
                ("Exportar GIF", self.export_gif),
                ("Exportar Imagem", self.export_image),
            ],
            bottom_padding=0,
        )

        self.status_var = tk.StringVar(value="Pronto para analisar polos e zeros.")
        ttk.Label(parent, textvariable=self.status_var, wraplength=320, background="#17212b", foreground="#94a3b8").pack(anchor="w", pady=(16, 0))

    def _build_section(self, parent, title, subtitle, fields, buttons, bottom_padding):
        section = ttk.Frame(parent, style="Card.TFrame")
        section.pack(fill="x", pady=(0, bottom_padding))

        ttk.Label(section, text=title, background="#17212b", foreground="#f8fafc", font=("Segoe UI Semibold", 13)).pack(anchor="w")
        ttk.Label(section, text=subtitle, background="#17212b", foreground="#94a3b8", wraplength=320).pack(anchor="w", pady=(2, 10))

        for label, var in fields:
            ttk.Label(section, text=label, background="#17212b", foreground="#cbd5e1").pack(anchor="w", pady=(8, 4))
            ttk.Entry(section, textvariable=var, width=42).pack(fill="x")

        button_frame = ttk.Frame(section, style="Card.TFrame")
        button_frame.pack(fill="x", pady=(16, 0))

        for index, (label, command) in enumerate(buttons):
            style = "Accent.TButton" if index == 0 and title == "Análise principal" else None
            button_kwargs = {"text": label, "command": command}
            if style is not None:
                button_kwargs["style"] = style
            ttk.Button(button_frame, **button_kwargs).pack(fill="x", pady=4)

    def _build_output(self, parent):
        ttk.Label(parent, text="Mapa e explicação do sistema", background="#17212b", foreground="#f8fafc", font=("Segoe UI Semibold", 14)).pack(anchor="w")
        self.text = scrolledtext.ScrolledText(
            parent,
            wrap=tk.WORD,
            font=("Consolas", 11),
            bg="#0b1220",
            fg="#e2e8f0",
            insertbackground="#e2e8f0",
            relief="flat",
            padx=12,
            pady=12,
        )
        self.text.pack(fill="both", expand=True, pady=(12, 0))
        self.text.insert("end", "O resultado da análise aparece aqui depois de clicar em Analisar sistema.\n")
        self.text.config(state="disabled")

    def _parse_tf(self):
        numerator = ast.literal_eval(self.numerator_var.get())
        denominator = ast.literal_eval(self.denominator_var.get())
        return TransferFunction(list(numerator), list(denominator))

    def _parse_list_or_expr(self, value):
        try:
            parsed = ast.literal_eval(value)
            return list(parsed) if not isinstance(parsed, list) else parsed
        except Exception:
            return list(eval(value, {"__builtins__": {}}, {"range": range, "x": 0}))

    def _parse_complex_value(self, value):
        try:
            parsed = ast.literal_eval(value)
        except Exception:
            parsed = eval(value, {"__builtins__": {}}, {"j": 1j, "complex": complex})

        if isinstance(parsed, (int, float, complex)):
            return complex(parsed)
        raise ValueError("O centro do zoom deve ser um número real ou complexo.")

    def _parse_variable_symbol(self):
        symbol = self.variable_var.get().strip()
        return symbol if symbol else "s"

    def _parse_float_value(self, value):
        try:
            return float(ast.literal_eval(value))
        except Exception:
            return float(value)

    def _format_complex_value(self, value):
        if abs(value.imag) < 1e-12:
            return f"{value.real:g}"
        return f"{value.real:g}{value.imag:+g}j"

    def _refresh_text(self, content):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("end", content)
        self.text.config(state="disabled")

    def _show_time_plot(self, t, y, title):
        fig, _ax = plot_time_response(t, y, title=title)
        self.last_fig = fig
        try:
            plt.show()
        except Exception:
            pass

    def analyze(self):
        try:
            tf = self._parse_tf()
            explanation = explain_system(tf, variable_symbol=self._parse_variable_symbol())
            self._refresh_text(explanation)
            self.status_var.set("Sistema analisado. Foco em polos, zeros e comportamento local.")
        except Exception as exc:
            messagebox.showerror("Erro de análise", str(exc))

    def show_poles_zeros(self):
        try:
            tf = self._parse_tf()
            fig, _ax = plot_pole_zero_map(tf.zeros, tf.poles)
            self.last_fig = fig
            try:
                plt.show()
            except Exception:
                pass
            self.status_var.set("Mapa de polos e zeros aberto no Matplotlib.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def show_poles_zeros_zoom(self):
        try:
            tf = self._parse_tf()
            center = self._parse_complex_value(self.zoom_center_var.get())
            span = float(self.zoom_span_var.get())
            fig, _ax = plot_pole_zero_zoom(tf.zeros, tf.poles, center=center, span=span)
            self.last_fig = fig
            try:
                plt.show()
            except Exception:
                pass
            self.status_var.set(f"Zoom de polos e zeros aberto em torno de {self._format_complex_value(center)}.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def show_step(self):
        try:
            tf = self._parse_tf()
            t_max = float(self.tmax_var.get())
            dt = float(self.dt_var.get())
            t, y = step_response(tf, t_max, dt)
            self._show_time_plot(t, y, "Resposta ao degrau unitário")
            self.status_var.set("Resposta ao degrau unitário aberta no Matplotlib.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def show_impulse(self):
        try:
            tf = self._parse_tf()
            t_max = float(self.tmax_var.get())
            dt = float(self.dt_var.get())
            t, y = impulse_response(tf, t_max, dt)
            self._show_time_plot(t, y, "Resposta ao impulso unitário")
            self.status_var.set("Resposta ao impulso aberta no Matplotlib.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def show_ramp(self):
        try:
            tf = self._parse_tf()
            t_max = float(self.tmax_var.get())
            dt = float(self.dt_var.get())
            t, y = arbitrary_input_response(tf, t_max, dt, lambda time_value: time_value)
            self._show_time_plot(t, y, "Resposta à rampa unitária")
            self.status_var.set("Resposta à rampa aberta no Matplotlib.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def show_root_locus(self):
        try:
            tf = self._parse_tf()
            gains = self._parse_list_or_expr(self.gains_var.get())
            zeta = self._parse_float_value(self.zeta_var.get())
            fig, _ax = plot_root_locus_with_zeta(root_locus(tf, gains), zeta=zeta)
            self.last_fig = fig
            try:
                plt.show()
            except Exception:
                pass
            self.status_var.set("Lugar das raízes com linha de ζ aberto no Matplotlib.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def export_gif(self):
        try:
            tf = self._parse_tf()
            output = filedialog.asksaveasfilename(
                title="Salvar GIF didático",
                defaultextension=".gif",
                filetypes=[("GIF", "*.gif")],
            )
            if not output:
                return
            variable_symbol = self._parse_variable_symbol()
            create_calculation_gif(tf, output, title=f"Processo de Cálculo em {variable_symbol}", variable_symbol=variable_symbol)
            self.status_var.set(f"GIF salvo em {Path(output).name}.")
        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def export_image(self):
        try:
            if not hasattr(self, "last_fig") or self.last_fig is None:
                messagebox.showwarning("Nenhuma figura", "Nenhuma figura gerada ainda para exportar.")
                return
            output = filedialog.asksaveasfilename(
                title="Salvar imagem do gráfico",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg")],
            )
            if not output:
                return
            self.last_fig.savefig(output, dpi=150)
            self.status_var.set(f"Imagem salva em {Path(output).name}.")
        except Exception as exc:
            messagebox.showerror("Erro ao exportar imagem", str(exc))


def launch_app():
    app = ControlApp()
    app.mainloop()