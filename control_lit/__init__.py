"""Biblioteca local para análise de sistemas LIT."""

from .math_utils import (
    add_polynomials,
    convolve,
    normalize_polynomial,
    polynomial_scale,
    polynomial_derivative,
    polynomial_roots,
    polynomial_to_string,
    polyval,
    trim_polynomial,
)
# frequency response utilities were moved to control_lit/deprecated/
# to de-emphasize Bode/Nyquist in the main API surface.
from .input_response import arbitrary_input_response
from .transfer_function import TransferFunction
from .time_response import impulse_response, step_response
from .root_locus import root_locus
from .plotting import plot_pole_zero_map, plot_pole_zero_zoom

__all__ = [
    "TransferFunction",
    "arbitrary_input_response",
    "add_polynomials",
    "convolve",
    "impulse_response",
    "normalize_polynomial",
    "polynomial_derivative",
    "polynomial_roots",
    "polynomial_scale",
    "polynomial_to_string",
    # frequency response functions intentionally omitted from public API
    "polyval",
    "plot_pole_zero_map",
    "plot_pole_zero_zoom",
    "root_locus",
    "step_response",
    "trim_polynomial",
]