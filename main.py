"""Exemplo de uso da biblioteca local control_lit."""

from control_lit import TransferFunction, root_locus, step_response
from control_lit.plotting import plot_root_locus, plot_step_response


def main():
    system = TransferFunction([1.0], [1.0, 2.0, 1.0])

    print("Polos:", system.poles)
    print("Zeros:", system.zeros)

    t, y = step_response(system, t_max=10.0, dt=0.01)
    plot_step_response(t, y)

    gains = [index * 0.2 for index in range(51)]
    roots_data = root_locus(system, gains)
    plot_root_locus(roots_data)

    import matplotlib.pyplot as plt

    plt.show()


if __name__ == "__main__":
    main()