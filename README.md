

Resumo rápido
------------
Projeto pedagógico em Python para análise de sistemas lineares invariantes no tempo (LIT). Foco atual: análise de polos/zeros, Lugar das Raízes, zoom localizado e simulações temporais (RK4). Rotinas de Bode/Nyquist foram movidas para `control_lit.deprecated` e não aparecem por padrão na GUI.

Principais módulos
------------------
- `control_lit/math_utils.py` — operações polinomiais e Durand–Kerner (raízes).
- `control_lit/transfer_function.py` — classe `TransferFunction`, álgebra e conversão para espaço de estados.
- `control_lit/time_response.py` / `control_lit/input_response.py` — RK4 para resposta ao tempo e entradas arbitrárias.
- `control_lit/root_locus.py` — cálculo iterativo do Lugar das Raízes via amostragem de ganho.
- `control_lit/plotting.py` — plots focados em polos/zeros, zoom e root-locus com linha de ζ.
- `control_lit/analysis_explainer.py` — gera laudos textuais e passos para GIFs; variável simbólica parametrizável (`s`, `z`, ...).
- `control_lit/gif_tools.py` — exportação de GIFs pedagógicos.
- `control_lit/gui.py` — interface Tkinter (principal ponto de uso).

Nota sobre funcionalidades de frequência
--------------------------------------
As rotinas de avaliação em frequência e plot Bode/Nyquist foram arquivadas em `control_lit/deprecated/` para não poluir o fluxo principal. Se precisar usar essas ferramentas, importe diretamente:

```py
from control_lit.deprecated.frequency_response import bode_data, nyquist_data
from control_lit.deprecated.plotting_bode import plot_bode, plot_nyquist
```

Instalação (recomendada)
------------------------
Crie um ambiente e instale dependências mínimas (ex.: matplotlib, pillow):

```bash
conda create -n lit-env python=3.10 -y
conda activate lit-env
pip install -r requirements.txt
# ou, se não houver requirements.txt
pip install matplotlib pillow
```

Executando a GUI
----------------
No diretório do projeto, execute:

```bash
python app.py
```

ou para testar apenas a importação do módulo GUI (não abre a janela):

```bash
python -c "from control_lit.gui import launch_app; print('GUI import OK')"
```

Exemplos úteis (para figuras no README/documento)
-------------------------------------------------
1. Exemplo para mostrar o mapa global (coefs prontos para colar na GUI):
   - Numerador: `[1, 4]`
   - Denominador: `[1, 28.5, 186, 326, 120]`
   - Interpretação: polos bem espalhados e um zero isolado — bom para visão global.

2. Exemplo para testar zoom / quase-cancelamento (cole na GUI):
   - Numerador: `[1, 2.01]`
   - Denominador: `[1, 9.02, 24.14, 20.2]`  # corresponde a (s+2)(s+2.02)(s+5)
   - Versão mais dramática: numerador `[1, 2.001]` e denom com `2.002` em vez de `2.02`.

Fluxo sugerido para gerar as imagens:
- Abra a GUI (`python app.py`).
- Cole os coeficientes em "Numerador" / "Denominador" e clique em "Analisar sistema".
- Use "Plotar polos e zeros" para mapa global.
- Use "Zoom polos/zeros" com `Centro = -2+0j` e `Janela = 0.5` para inspecionar o agrupamento.
- Para o Lugar das Raízes, preencha "Ganhos K" (ex.: `[x * 0.2 for x in range(51)]`) e clique em "Plotar Root Locus com ζ".
- Exporte imagens com "Exportar Imagem" ou GIFs com "Exportar GIF".

Testes
------
Há uma suíte de testes em `tests/` usando `unittest`. Para rodar os testes:

```bash
python -m unittest discover -v
```
