import os
import tempfile
import unittest

from control_lit import TransferFunction, arbitrary_input_response, root_locus, step_response
from control_lit.deprecated.frequency_response import bode_data, nyquist_data
from control_lit.analysis_explainer import _format_complex, explain_system
from control_lit.gif_tools import create_calculation_gif
from control_lit.math_utils import add_polynomials, convolve, polynomial_roots, polynomial_to_string


class MathUtilsTests(unittest.TestCase):
    def test_add_and_convolve(self):
        self.assertEqual(add_polynomials([1, 2, 1], [1, 1]), [1, 3, 2])
        self.assertEqual(convolve([1, 2], [1, 1]), [1, 3, 2])

    def test_polynomial_roots(self):
        roots = polynomial_roots([1, 2, 1])
        self.assertEqual(len(roots), 2)
        self.assertTrue(all(abs(root + 1) < 1e-6 for root in roots))

    def test_polynomial_string(self):
        self.assertEqual(polynomial_to_string([1, 0, 1]), "1s^2 + 1")


class TransferFunctionTests(unittest.TestCase):
    def test_poles_and_closed_loop(self):
        tf = TransferFunction([1], [1, 2, 1])
        self.assertEqual(len(tf.poles), 2)
        closed_loop = tf.feedback()
        self.assertIsInstance(closed_loop, TransferFunction)

    def test_explainer_has_eight_steps_with_results(self):
        tf = TransferFunction([1], [1, 2, 1])
        report = explain_system(tf)
        self.assertIn("1) Escrever N(s) e D(s)", report)
        self.assertIn("8) Resumo final", report)
        self.assertIn("Polos (brutos)", report)
        self.assertIn("Zeros (brutos)", report)

    def test_complex_formatter_preserves_tiny_imaginary_part(self):
        text = _format_complex(complex(2.76205, 1.2246467991473532e-16))
        self.assertIn("e-16j", text)


class ResponseTests(unittest.TestCase):
    def test_step_response_shape(self):
        tf = TransferFunction([1], [1, 2, 1])
        t, y = step_response(tf, 1.0, 0.1)
        self.assertEqual(len(t), len(y))
        self.assertGreater(len(t), 0)

    def test_arbitrary_pulse_response(self):
        tf = TransferFunction([1], [1, 2, 1])
        t, y = arbitrary_input_response(tf, 1.0, 0.1, [0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0])
        self.assertEqual(len(t), len(y))

    def test_frequency_helpers(self):
        tf = TransferFunction([1], [1, 2, 1])
        mag, phase = bode_data(tf, [0.1, 1, 10])
        points = nyquist_data(tf, [0.1, 1, 10])
        self.assertEqual(len(mag), 3)
        self.assertEqual(len(phase), 3)
        self.assertGreaterEqual(len(points), 3)

    def test_root_locus(self):
        tf = TransferFunction([1], [1, 2, 1])
        data = root_locus(tf, [0, 1, 2])
        self.assertEqual(len(data), 3)


class GifTests(unittest.TestCase):
    def test_create_gif(self):
        tf = TransferFunction([1], [1, 2, 1])
        with tempfile.TemporaryDirectory() as temp_dir:
            output = os.path.join(temp_dir, "calc.gif")
            create_calculation_gif(tf, output)
            self.assertTrue(os.path.exists(output))
            self.assertGreater(os.path.getsize(output), 0)


if __name__ == "__main__":
    unittest.main()