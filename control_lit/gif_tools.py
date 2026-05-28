"""Geração de GIFs didáticos usando Pillow. (fiz isso apenas para mostrar o processo de análise passo a passo, e gerar um texto explicativo detalhado. Não é essencial, mas eu quis)"""

from __future__ import annotations

from math import ceil

from PIL import Image, ImageDraw, ImageFont

from .analysis_explainer import build_gif_steps


def _load_font(size):
    candidates = [
        "arial.ttf",
        "DejaVuSans.ttf",
    ]
    for name in candidates:
        try:
            return ImageFont.truetype(name, size=size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def create_calculation_gif(tf, output_path, title="Processo de Cálculo", size=(960, 560), duration=900, variable_symbol="s"):
    """Cria um GIF textual com os passos centrais do cálculo."""

    steps = build_gif_steps(tf, variable_symbol=variable_symbol)
    font_title = _load_font(34)
    font_body = _load_font(24)
    font_small = _load_font(18)

    frames = []
    for index, step in enumerate(steps):
        image = Image.new("RGB", size, color=(18, 28, 38))
        draw = ImageDraw.Draw(image)

        draw.rounded_rectangle((24, 24, size[0] - 24, size[1] - 24), radius=28, outline=(88, 182, 255), width=4, fill=(24, 38, 52))
        draw.text((54, 44), title, fill=(240, 248, 255), font=font_title)

        progress_width = size[0] - 120
        draw.rounded_rectangle((60, 112, 60 + progress_width, 128), radius=8, outline=(120, 140, 160), width=2)
        fill_width = int(progress_width * ((index + 1) / len(steps)))
        draw.rounded_rectangle((60, 112, 60 + fill_width, 128), radius=8, fill=(86, 198, 142))
        draw.text((60, 138), f"Etapa {index + 1} de {len(steps)}", fill=(170, 190, 210), font=font_small)

        wrapped = _wrap_text(draw, step, font_body, size[0] - 120)
        y = 208
        for line in wrapped:
            draw.text((60, y), line, fill=(245, 245, 245), font=font_body)
            y += 34

        draw.text((60, size[1] - 84), "Biblioteca local LIT | cálculo simbólico didático", fill=(170, 190, 210), font=font_small)
        frames.append(image)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0,
        disposal=2,
    )


def create_root_locus_gif(tf, gains, output_path):
    """Cria um GIF simples do deslocamento das raízes ao longo dos ganhos."""

    from .root_locus import root_locus

    roots_data = root_locus(tf, gains)
    steps = []
    for entry in roots_data:
        roots_text = ", ".join(f"{root.real:.3f}{root.imag:+.3f}j" for root in entry["roots"])
        steps.append(f"K = {entry['K']:.3f} | raízes: {roots_text}")

    class _StubTF:
        pass

    stub = _StubTF()
    stub.numerator = tf.numerator
    stub.denominator = tf.denominator
    stub.poles = tf.poles
    stub.zeros = tf.zeros
    build_gif = build_gif_steps(stub)
    build_gif.extend(steps)
    create_calculation_gif(stub, output_path, title="Root Locus - Processo", duration=700)