.PHONY: init create update test destroy deploy

.DEFAULT: help
help:
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
CONDA_ENV=conda run -n ${ENV} --no-capture-output

UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	CONDA_LOCK=conda-linux-64.lock
endif
ifeq ($(UNAME_S),Darwin)
	CONDA_LOCK=conda-osx-arm64.lock
endif

create:
	conda create -n ${ENV} --file ${CONDA_LOCK}
	${CONDA_ENV} poetry install
	${CONDA_ENV} pre-commit install

update:
	conda-lock --mamba -f environment.yaml -k explicit
	${CONDA_ENV} conda update --file ${CONDA_LOCK}

test:
	${CONDA_ENV} pytest -n auto

deploy:
	rm -rf dist/
	${CONDA_ENV} python3 setup.py sdist bdist_wheel
	${CONDA_ENV} twine upload dist/*

destroy:
	conda env remove -n ${ENV}

# dev utilities
init:
	conda-lock --mamba -f environment.yaml -k explicit

fortran:
	f2py -c -m prosail prosail/MODULE_PRO4SAIL.f90 prosail/dataSpec_PDB.f90 prosail/main_PROSAIL.f90 prosail/LIDF.f90 prosail/dladgen.f prosail/PRO4SAIL.f90 prosail/prospect_DB.f90 prosail/tav_abs.f90 prosail/volscatt.f90 \
		&& mv *.so xleaf/

pypi:
	rm -rf dist/
	${CONDA_ENV} poetry build
	twine upload dist/*
