#!/usr/bin/env python
import argparse
import dataclasses
import pathlib
import subprocess
import tempfile
import venv


@dataclasses.dataclass
class Requirements:
    requirements: pathlib.Path
    name: str = None
    freeze_file: pathlib.Path = None
    install_args: list[str] = None
    freeze_args: list[str] = None
    _args: dict[dict[str, list[str]]] = dataclasses.field(default_factory=dict)

    def __post_init__(self) -> None:
        self._args = {
            "install": {
                "units": ["--editable", "."],
            },
            "freeze": {
                "units": ["--exclude-editable"],
            },
        }
        self.name = self.requirements.stem
        self.freeze_file = pathlib.Path(self.requirements).with_suffix(".txt")
        self.install_args = self._args["install"].get(self.name, [])
        self.freeze_args = self._args["freeze"].get(self.name, [])

    def freeze(self) -> None:
        with tempfile.TemporaryDirectory() as venv_tmpdir:
            freezer_venv = pathlib.Path(venv_tmpdir)
            venv_python = freezer_venv / "bin" / "python"
            pip = [venv_python, "-m", "pip", "--disable-pip-version-check"]

            venv.create(freezer_venv, clear=True, with_pip=True)
            subprocess.run([*pip, "install", "-r", self.requirements, *self.install_args], env={})
            out = subprocess.check_output([*pip, "freeze", *self.freeze_args], env={}, text=True)

        self.freeze_file.write_text(out)


def requirements_factory():
    reqs = []
    for file in pathlib.Path("tests/requirements").glob("*.in"):
        reqs.append(Requirements(file))

    return reqs


def main():
    requirements: list[Requirements] = requirements_factory()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--test",
        dest="requested_tests",
        help="Name of test requirements to freeze",
        action="append",
        choices=[file.name for file in requirements],
    )
    args = parser.parse_args()

    requested_files: set[str] = set(args.requested_tests or [])
    requirements = [req for req in requirements if req.name in requested_files] if requested_files else requirements

    for file in requirements:
        print(f"=== Freezing {file.name} requirements at {file.freeze_file} ===")
        file.freeze()


if __name__ == "__main__":
    main()
