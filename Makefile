help:
	@echo "Please use \`make <target>' where <target> is one of:"
	@echo "  help                        show this message."
	@echo "  lint                        run pre-commit on all files."
	@echo "  requirements                refresh installed packages to match lock file."
	@echo "  upgrade-requirements        update all packages in lock file."


lint:
	uv run pre-commit run --all-files

requirements:
	uv sync --all-groups

upgrade-requirements:
	uv sync --upgrade --all-groups
