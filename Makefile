.DEFAULT_GOAL := help
.PHONY: install check pytest pylint pyright style black isort help

install: ## Install/Upgrade all dependencies in editable/developer mode
	pip install --upgrade -e '.[dev]'

check: pytest pylint pyright ## Run pytest, pylint, and pyright

pytest: ## Execute unit tests with pytest
	python -m pytest -s

pylint: ## Check code smells with pylint
	python -m pylint --exit-zero src

pyright: ## Check type annotations
	python -m pyright

style: black isort ## Run black and isort

black: ## Auto-format python code using black
	python -m black src

isort: ## Auto-format python code using isort
	python -m isort src

help: # Run `make help` to get help on the make commands
	@echo "\033[36mAvailable commands:\033[0m"
	@fgrep "##" Makefile | fgrep -v fgrep
