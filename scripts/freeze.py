#!/usr/bin/env python
import pathlib
import subprocess
import tempfile
import venv


def main():
    requirements = pathlib.Path("tests/requirements.in")

    with tempfile.TemporaryDirectory() as venv_tmpdir:
        freezer_venv = pathlib.Path(venv_tmpdir)
        venv_python = freezer_venv / "bin" / "python"
        pip = [venv_python, "-m", "pip", "--disable-pip-version-check"]

        venv.create(freezer_venv, clear=True, with_pip=True)
        subprocess.run([*pip, "install", "-r", requirements], env={})
        out = subprocess.check_output([*pip, "freeze"], env={}, text=True)
        requirements.with_suffix(".txt").write_text(out)


if __name__ == "__main__":
    main()
