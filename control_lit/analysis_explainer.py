"""Gera explicações textuais passo a passo para a interface e GIFs."""

from __future__ import annotations

from .math_utils import normalize_polynomial, polynomial_to_string, polyval


def _normalize_variable_symbol(variable_symbol):
    variable_symbol = str(variable_symbol).strip()
    return variable_symbol if variable_symbol else "s"


def _format_float(value, decimals=6, tiny=1e-12):
    if value == 0:
        return "0"

    rounded = round(value, decimals)
    """Isso aqui é pra n ficar zero lá no texto, mas arredondar legalmente pra não ter um monte de zeros depois da vírgula. Se o valor for muito pequeno, a notação científica é mais clara."""
    if rounded == 0 and abs(value) < tiny:
        return f"{value:.3e}"
    return f"{rounded:g}"


def _format_complex(value, decimals=6):
    real_txt = _format_float(value.real, decimals=decimals)
    imag_abs_txt = _format_float(abs(value.imag), decimals=decimals)
    sign = "+" if value.imag >= 0 else "-"
    return f"{real_txt} {sign} {imag_abs_txt}j"


def _group_roots(roots, tol=1e-5):
    groups = []
    for root in roots:
        found = None
        for group in groups:
            if abs(root - group["center"]) <= tol:
                found = group
                break
        if found is None:
            groups.append({"center": root, "roots": [root]})
        else:
            found["roots"].append(root)
            found["center"] = sum(found["roots"]) / len(found["roots"])
    return groups

"""Detecta cancelamentos aproximados entre grupos de zeros e polos, retornando a raiz de cancelamento e sua ordem, bem óbvio pelo nome mas botei comentário em todas as coisas pra ficar mais fácil na apresentação"""
def _detect_cancellations(zero_groups, pole_groups, tol=1e-4):
    cancellations = []
    pole_remaining = [len(group["roots"]) for group in pole_groups]
    zero_remaining = [len(group["roots"]) for group in zero_groups]

    for i, zero_group in enumerate(zero_groups):
        for j, pole_group in enumerate(pole_groups):
            if abs(zero_group["center"] - pole_group["center"]) <= tol:
                amount = min(zero_remaining[i], pole_remaining[j])
                if amount > 0:
                    cancellations.append(
                        {
                            "root": (zero_group["center"] + pole_group["center"]) / 2,
                            "count": amount,
                        }
                    )
                    zero_remaining[i] -= amount
                    pole_remaining[j] -= amount
    return cancellations

''' Isso aqui foi basicamente para demonstrar o processo de análise passo a passo, e gerar um texto explicativo detalhado. Ele não é otimizado nem nada, apenas fiz isso para que o que eu comentei na sala fosse bem explicado.'''
def explain_system(tf, omega_sample=None, gain_sample=1.0, variable_symbol="s"):
    omega_sample = omega_sample if omega_sample is not None else [0.1, 1.0, 10.0]
    variable_symbol = _normalize_variable_symbol(variable_symbol)

    zeros = tf.zeros
    poles = tf.poles

    zero_groups = _group_roots(zeros)
    pole_groups = _group_roots(poles)
    cancellations = _detect_cancellations(zero_groups, pole_groups)

    den_normalized = normalize_polynomial(tf.denominator)
    lead = tf.denominator[0]

    lines = []
    lines.append("Analise passo a passo para polos e zeros (8 etapas)")
    lines.append("=" * 66)
    lines.append("")

    lines.append(f"1) Escrever N({variable_symbol}) e D({variable_symbol}) com coeficientes ordenados por grau")
    lines.append(f"   N coef = {tf.numerator}")
    lines.append(f"   D coef = {tf.denominator}")
    lines.append(f"   N({variable_symbol}) = {polynomial_to_string(tf.numerator, variable=variable_symbol)}")
    lines.append(f"   D({variable_symbol}) = {polynomial_to_string(tf.denominator, variable=variable_symbol)}")
    lines.append("")

    lines.append("2) Normalizar o denominador (coeficiente lider igual a 1)")
    if abs(lead - 1.0) < 1e-12:
        lines.append(f"   D({variable_symbol}) ja estava normalizado.")
    else:
        lines.append(f"   Coeficiente lider encontrado: {lead:g}")
        lines.append(f"   D_norm coef = {den_normalized}")
        lines.append(f"   D_norm({variable_symbol}) = {polynomial_to_string(den_normalized, variable=variable_symbol)}")
    lines.append("")

    lines.append(f"3) Aplicar Durand-Kerner em N({variable_symbol}) para zeros candidatos")
    if zeros:
        for index, root in enumerate(zeros, start=1):
            lines.append(f"   z{index} = {_format_complex(root)}")
    else:
        lines.append("   Nao ha zeros finitos (numerador constante).")
    lines.append("")

    lines.append(f"4) Aplicar Durand-Kerner em D({variable_symbol}) para polos candidatos")
    if poles:
        for index, root in enumerate(poles, start=1):
            lines.append(f"   p{index} = {_format_complex(root)}")
    else:
        lines.append("   Nao ha polos finitos (caso degenerado).")
    lines.append("")

    lines.append("5) Detectar cancelamentos zero-polo por tolerancia")
    if cancellations:
        for item in cancellations:
            lines.append(f"   Cancelamento em {_format_complex(item['root'])} (ordem {item['count']})")
    else:
        lines.append("   Nenhum cancelamento detectado com tolerancia 1e-4.")
    lines.append("")

    lines.append("6) Determinar multiplicidades por agrupamento de raizes proximas")
    if zero_groups:
        lines.append("   Zeros agrupados:")
        for group in zero_groups:
            lines.append(f"   - {_format_complex(group['center'])} | multiplicidade {len(group['roots'])}")
    else:
        lines.append("   Zeros agrupados: nenhum")

    if pole_groups:
        lines.append("   Polos agrupados:")
        for group in pole_groups:
            lines.append(f"   - {_format_complex(group['center'])} | multiplicidade {len(group['roots'])}")
    else:
        lines.append("   Polos agrupados: nenhum")
    lines.append("")

    lines.append(f"7) Verificar comportamento local avaliando N({variable_symbol})/D({variable_symbol}) perto das raizes")
    epsilon = 1e-4
    if zeros:
        for index, root in enumerate(zeros, start=1):
            probe = root + epsilon
            num_val = polyval(tf.numerator, probe)
            den_val = polyval(tf.denominator, probe)
            ratio_txt = "indefinido" if abs(den_val) < 1e-14 else f"{abs(num_val / den_val):.3e}"
            lines.append(
                f"   Zero z{index}: |N(z+eps)|={abs(num_val):.3e}, |D(z+eps)|={abs(den_val):.3e}, |G(z+eps)|~{ratio_txt}"
            )
    if poles:
        for index, root in enumerate(poles, start=1):
            probe = root + epsilon
            num_val = polyval(tf.numerator, probe)
            den_val = polyval(tf.denominator, probe)
            ratio_txt = "muito grande" if abs(den_val) < 1e-10 else f"{abs(num_val / den_val):.3e}"
            lines.append(
                f"   Polo p{index}: |N(p+eps)|={abs(num_val):.3e}, |D(p+eps)|={abs(den_val):.3e}, |G(p+eps)|~{ratio_txt}"
            )
    lines.append("")

    lines.append("8) Resumo final")
    lines.append(f"   Zeros (brutos): {[ _format_complex(z) for z in zeros ] if zeros else 'nenhum'}")
    lines.append(f"   Polos (brutos): {[ _format_complex(p) for p in poles ] if poles else 'nenhum'}")
    if cancellations:
        cancel_text = [f"{_format_complex(c['root'])} (ordem {c['count']})" for c in cancellations]
    else:
        cancel_text = "nenhum"
    lines.append(f"   Cancelamentos: {cancel_text}")
    lines.append("   Conclusao: use a localizacao dos polos remanescentes para avaliar estabilidade e dinamica.")
    lines.append("")

    lines.append("Complemento da analise")
    lines.append("-" * 66)
    lines.append("Resposta temporal")
    lines.append("A resposta é obtida integrando a forma canônica controlável com RK4.")
    lines.append("")
    lines.append("Resposta em frequencia (SECUNDÁRIO)")
    lines.append(f"Opcionalmente avaliamos G(jω) para ω em {omega_sample} para análise em frequência.")
    lines.append("Essas rotinas de Bode/Nyquist foram movidas para o módulo `control_lit.deprecated` e não são exibidas por padrão na GUI.")
    lines.append("")
    lines.append("")
    lines.append("Lugar das raizes")
    lines.append(f"Equação característica: D({variable_symbol}) + K·N({variable_symbol}) = 0, com K = {gain_sample:g} como exemplo.")

    return "\n".join(lines)

"""O passo a passo de criação do processo de análise é basicamente para mostrar o processo de análise detalhado, e gerar um texto explicativo. Ele não é otimizado nem nada, apenas fiz isso para que o que eu comentei na sala fosse bem explicado."""
def build_gif_steps(tf, variable_symbol="s"):
    variable_symbol = _normalize_variable_symbol(variable_symbol)
    steps = [
        "Sistema recebido",
        f"G({variable_symbol}) = {polynomial_to_string(tf.numerator, variable=variable_symbol)} / {polynomial_to_string(tf.denominator, variable=variable_symbol)}",
    ]
    steps += [
        "Passos para encontrar polos e zeros:",
        f"1) Formular N({variable_symbol}) e D({variable_symbol})",
        "2) Normalizar denominador",
        f"3) Encontrar raízes de N({variable_symbol}) (zeros)",
        f"4) Encontrar raízes de D({variable_symbol}) (polos)",
        "5) Detectar cancelamentos",
        "6) Determinar multiplicidades",
        "7) Verificar avaliando o TF",
        "8) Resumir resultados",
    ]
    steps += [
        f"Polos calculados: {len(tf.poles)}",
        f"Zeros calculados: {len(tf.zeros)}",
        "Simulação numérica com RK4",
        "Bode: magnitude e fase",
        "Nyquist: plano complexo",
        "Root Locus: variação com K",
    ]
    return steps