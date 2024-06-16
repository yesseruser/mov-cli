.PHONY: build

PIP = pip
PYTHON = python

build:
	${PYTHON} -m build

build-system-packages:
	${PYTHON} -m build --wheel --no-isolation

install:
	${PIP} install . -U

install-editable:
	${PIP} install -e .[dev] --config-settings editable_mode=compat -U

test:
	ruff check --target-version=py38 .
