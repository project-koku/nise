def main():  # noqa: C901
    """Isolate globals from imported code"""

    import os
    import pathlib
    import sys
    import traceback

    from importlib import import_module

    def convert_relative_path_to_name(path: str) -> str:
        clean_path = pathlib.Path(path)
        if clean_path.name == "__init__.py":
            clean_path = clean_path.parent

        clean_path = clean_path.with_suffix("")
        name = str(clean_path).replace(os.path.sep, ".")

        return name

    def test_module(path: str, name: str, messages: set) -> None:
        try:
            import_module(name)
        except Exception as exc:
            exc_type, _exc, exc_tb = sys.exc_info()
            frames = reversed(traceback.extract_tb(exc_tb))
            line = 0
            message = str(exc)
            for frame in frames:
                if frame.filename.endswith(path):
                    line = frame.lineno or 0
                    break

            if message not in messages:
                messages.add(f"{path}:{line}: traceback: {exc_type.__name__} {message}")

    messages = set()
    files = sys.argv[1:]
    if not files:
        source_path = pathlib.Path("nise")
        files = [str(file) for file in source_path.rglob("*.py")]

    for path in files:
        name = convert_relative_path_to_name(path)
        test_module(path, name, messages)

    if messages:
        sys.exit("\n".join(messages))


if __name__ == "__main__":
    main()
