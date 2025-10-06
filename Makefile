## Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-eu -o pipefail -O inherit_errexit -c
.SILENT:clean
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules
NUL := >/dev/null 2>&1
# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
PYTHON?=python3

# installed?
ifeq (, $(shell which $(PYTHON) ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif

# version ok?
PYTHON_VERSION=$(shell $(PYTHON) -c "import sys; print(float(f'{sys.version_info[0]}.{sys.version_info[1]}'))")
PYTHON_VERSION_MIN=3.11
PYTHON_VERSION_OK=$(shell $(PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_VERSION_MIN)'.split('.'))))")

ifeq ($(PYTHON_VERSION_OK),False)
  $(error "Your Python version is $(PYTHON_VERSION). Required Python version >= $(PYTHON_VERSION_MIN).")
endif

PACKAGE_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
GIT_FOLDER=$(PACKAGE_FOLDER)/.git
VENV_FOLDER=$(PACKAGE_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin
ZOPE_VERSION=5.13

UV := $(shell command -v uv 2> /dev/null)
ifndef UV
	UV := $(UV)
endif

UVX := $(shell command -v uvx 2> /dev/null)
ifndef UVX
	UVX := $(UVX)
endif

.PHONY: all
all: help

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: # This help message
	@grep -E '^[a-zA-Z_-]+:.*?# .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?# "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: venv
venv: ## virtualenv
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)" 
	if [ ! -d $(VENV_FOLDER) ]; then 
		@$(PYTHON) -m venv $(VENV_FOLDER)
		@$(BIN_FOLDER)/pip3 install -U "pip" "uv"
		@$(UV) pip install horse-with-no-namespace
	fi

constraints-zope.txt: ## Generate constraints file
	@echo "$(GREEN)==> Generate constraints file$(RESET)"
	@echo '-c https://zopefoundation.github.io/Zope/releases/$(ZOPE_VERSION)/constraints.txt' > constraints-zope.txt

############################################
# Config
############################################
instance/etc/zope.ini instance/etc/zope.conf: ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	@$(UVX) cookiecutter -f --no-input -c 2.1.1 --config-file instance.yaml gh:plone/cookiecutter-zope-instance

.PHONY: config
config: instance/etc/zope.ini

############################################
# Installation
############################################
requirements-mxdev.txt: constraints-zope.txt ## Generate constraints file
	@echo "$(GREEN)==> Generate constraints file$(RESET)"
	@$(UVX) mxdev -c mx.ini

.PHONY: install
install: venv config constraints-zope.txt requirements-mxdev.txt ## Install Zope and dependencies
	@echo "$(GREEN)==> Install Zope and dependencies$(RESET)"
	@$(UV) pip install Paste -c constraints-zope.txt
	@$(UV) pip install Products.Sessions -c constraints-zope.txt
	@$(UV) pip install -r requirements-mxdev.txt

############################################
# Instance
############################################
.PHONY: start
start: venv instance/etc/zope.ini ## Start a Zope instance on localhost:8080
	@$(UV) run runwsgi instance/etc/zope.ini

.PHONY: zconsole
zconsole: $(VENV_FOLDER) instance/etc/zope.ini ## Start a console into a Zope instance
	@$(UV) run zconsole debug instance/etc/zope.conf

############################################
# QA
############################################
.PHONY: pre-commit
pre-commit: venv ## pre-commit install
	@echo "$(GREEN)==> pre-commit$(RESET)"
	@$(UVX) pre-commit install

.PHONY: lint
lint: venv ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Lint codebase$(RESET)"
	@$(UVX) ruff@latest check --fix --config pyproject.toml
	@$(UVX) pyroma@latest -d .
	@$(UVX) check-python-versions@latest .
	@$(UVX) zpretty@latest --check src

.PHONY: format
format: venv ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	@$(UVX) ruff@latest check --fix --config pyproject.toml
	@$(UVX) ruff@latest format --config pyproject.toml
	@$(UVX) zpretty@latest -i src

.PHONY: manifest
manifest: venv ## Check Manifest
	@echo "$(GREEN)==> Check Manifest$(RESET)"
	@$(UVX) check-manifest@latest -v

.PHONY: check
check: format lint manifest ## Check and fix code base according to Plone standards

############################################
# Tests
############################################
.PHONY: test
test: venv ## run tests
	@echo "$(GREEN)==> Running tests$(RESET)"
	@$(UV) export --format requirements-txt --extra test -o requirements-test.txt
	@$(UV) pip install -r requirements-test.txt
	@$(UV) pip install horse-with-no-namespace
	@rm requirements-test.txt
	@$(UV) run pytest --disable-warnings

.PHONY: test-coverage
test-coverage: venv ## run tests with coverage
	@echo "$(GREEN)==> Running tests$(RESET)"
	@$(UV) export --format requirements-txt --extra test -o requirements-test.txt $(NUL)
	@$(UV) pip install -r requirements-test.txt $(NUL)
	@$(UV) pip install horse-with-no-namespace
	@rm requirements-test.txt
	@$(UV) run pytest --cov=Products.mcdutils --cov-report term-missing --cov-report=html:coverage-html-report

############################################
# Docs
############################################
.PHONY: docs
docs: venv ## Building the documentation
	@echo "$(GREEN)==> Building the documentation$(RESET)"
	@$(UV) export --format requirements-txt --extra docs -o requirements-docs.txt $(NUL)
	@$(UV) pip install -r requirements-docs.txt $(NUL)
	@rm requirements-docs.txt
	@$(UV) run sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html

.PHONY: watch-docs
watch-docs: venv ## Watchiling docs
	@echo "$(GREEN)==> Watchiling docs$(RESET)"
	@$(UV) export --format requirements-txt --extra docs -o requirements-docs.txt $(NUL)
	@$(UV) pip install -r requirements-docs.txt $(NUL)
	@rm requirements-docs.txt
	@$(UV) pip install sphinx-autobuild
	@$(UV) run sphinx-autobuild docs docs/_build/html

############################################
# Release
############################################
.PHONY: changelog
changelog: venv ## Release the package to pypi.org
	@echo "🚀 Display the draft for the changelog"
	@$(UV) pip install zestreleaser-towncrier==1.3.0
	@$(UV) run towncrier --draft --yes

.PHONY: release
release: venv ## Release the package
	@echo "🚀 Release package"
	@$(UV) pip install zest.releaser[recommended]==9.6.2
	@$(UV) run prerelease
	@$(UV) run release
	@rm -Rf dist
	@$(UV) build
#	@$(UV) publish
	@$(UV) run postrelease

############################################
# Dependency graph
############################################

.PHONY: dependency-graph
dependency-graph: venv ## Dependency graph
	@echo "📈 Dependency graph" 
	@$(UV) pip install horse pipdeptree graphviz
	@$(UV) run pipdeptree --exclude setuptools,wheel,pipdeptree,zope.interface,zope.component --graph-output svg > dependencies.svg

############################################
# Dependency circular
############################################

.PHONY: dependency-circular
dependency-circular: venv constraints-zope.txt## Dependency circular
	@echo "🔃 Dependency circular" 
	@$(UV) pip install horse pipdeptree
	@$(UV) pip install pipforester -c constraints-zope.txt
	@rm constraints-zope.txt
# 	Generate the full dependency tree
	@$(UV) run pipdeptree -j > forest.json
#	Generate a DOT graph with the circular dependencies, if any
	@$(UV) run pipforester -i forest.json -o forest.dot --cycles
#	Report if there are any circular dependencies, i.e. error if there are any
	@$(UV) run pipforester -i forest.json --check-cycles -o /dev/null

############################################
# Clean
############################################

.PHONY: clean
clean:  ## Clean
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	[ -f forest.dot ] && rm forest.dot
	[ -f forest.json ] && rm forest.json
	[ -f dependencies.svg ] && rm dependencies.svg
	[ -f constraints-zope.txt ] && rm constraints-zope.txt
	[ -f requirements-mxdev.txt ] && rm requirements-mxdev.txt
	[ -f requirements.txt ] && rm requirements.txt
	[ -f constraints-mxdev.txt ] && rm constraints-mxdev.txt
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -rf {} +
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name ".pytest_cache" -exec rm -rf {} +
	find . -name ".ruff_cache" -exec rm -rf {} +
	find . -name ".eggs" -exec rm -rf {} +
	find . -name "coverage-html-report" -exec rm -rf {} +
	find . -name ".venv" -exec rm -rf {} +
	find . -name "dist" -exec rm -rf {} +
	find . -name "build" -exec rm -rf {} +
	find . -name "instance" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "uv.lock" -delete
