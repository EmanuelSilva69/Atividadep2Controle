import tempfile
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from control_lit.gui import ControlApp


def main():
    # monkeypatch plt.show to avoid blocking
    plt_show_orig = plt.show
    plt.show = lambda *a, **k: None

    app = ControlApp()

    # set simple system
    app.numerator_var.set("[1]")
    app.denominator_var.set("[1, 2, 1]")
    # GUI simplified: remove frequency widgets (Bode/Nyquist). Set time/gain params.
    app.tmax_var.set("1.0")
    app.dt_var.set("0.1")
    app.gains_var.set("[0, 1, 2]")

    # replace file dialogs to save to temp files
    tmpdir = tempfile.gettempdir()

    import tkinter.filedialog as fd
    fd_asksave_orig = fd.asksaveasfilename
    fd.asksaveasfilename = lambda **kwargs: os.path.join(tmpdir, 'test_output.' + (kwargs.get('defaultextension') or 'png').lstrip('.'))

    try:
        app.analyze()
        print('analyze OK')
        # Bode/Nyquist removed from GUI; exercise other flows instead
        app.show_step()
        print('step OK')
        app.show_root_locus()
        print('root locus OK')
        # export GIF and image
        app.export_gif()
        print('export gif OK')
        # ensure last_fig set by previous plotting; if not, generate one
        if not hasattr(app, 'last_fig') or app.last_fig is None:
            app.show_step()
        app.export_image()
        print('export image OK')
    finally:
        # restore
        fd.asksaveasfilename = fd_asksave_orig
        plt.show = plt_show_orig
        app.destroy()


if __name__ == '__main__':
    main()
