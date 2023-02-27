.PHONY: init create update test destroy

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
	pip install -e .
	pre-commit install

test:
	${ENV_CONDA} pytest -n auto

destroy:
	conda env remove -n ${ENV}