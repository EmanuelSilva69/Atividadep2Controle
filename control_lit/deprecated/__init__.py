"""Módulo `deprecated` para funções movidas, mantido para referência histórica.

Conteúdo neste pacote pode ser removido em versões futuras.
"""

from .frequency_response import frequency_response, bode_data, nyquist_data

__all__ = ["frequency_response", "bode_data", "nyquist_data"]
