.PHONY: init create update test destroy deploy

.DEFAULT: help
help:
	@echo "make init"
	@echo "	initialize dev environment."
	@echo "make create"
	@echo "	create env and install dependencies."
	@echo "make update"
	@echo " update dependency versions"
	@echo "make test"
	@echo "	run module tests"
	@echo "make destroy"
	@echo " delete the current environment to start fresh"
	@echo "make deploy"
	@echo " upload package to pypi"

ENV=xleaf
PYTHON_VERSION=3.9
ENV_CONDA=conda run -n ${ENV} --no-capture-output

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	CONDA_LOCK=conda-linux-64.lock
endif
ifeq ($(UNAME_S),Darwin)
	CONDA_LOCK=conda-osx-arm64.lock
endif

init:
	conda-lock --mamba -f environment.yaml -k explicit

create:
	conda create -n ${ENV} --file ${CONDA_LOCK}
	${ENV_CONDA} pip install -e .
	${ENV_CONDA} pre-commit install

update:
	conda-lock --mamba -f environment.yaml -k explicit
	${ENV_CONDA} conda update --file ${CONDA_LOCK}

test:
	${ENV_CONDA} pytest -n auto

destroy:
	conda env remove -n ${ENV}

deploy:
	rm -rf dist/
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
