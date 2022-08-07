SHELL 		:= /bin/zsh

PIP_MODULES	:= pylint pydocstyle pycodestyle mypy rope

CACHE 		:= $(wildcard $(patsubst %, %/modules/**/__pycache__, .))
INITS		:= $(wildcard $(patsubst %, %/modules/*/__init__.py, .))
MODULES		:= $(patsubst ./modules/%/__init__.py, %, $(INITS))

VENV 		:= venv
PY			:= python3
PYTHON 		:= ./$(VENV)/bin/$(PY)

.DEFAULT_GOAL := test

$(VENV):
	$(PY) -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install $(PIP_MODULES)
	source $(VENV)/bin/activate

.git:
	git init
	git add .
	git commit -m "Create initial project"

.PHONY: init
init: $(VENV) .git

.PHONY: test
test: $(VENV)
	-$(RM) -r test/bin
	mkdir test/bin
	cd test/src; ../../sea.bash -d -o=../bin -m=t .

.PHONY: lint
lint: $(VENV)
	$(PYTHON) -m pylint --rcfile=.pylintrc $(MODULES)

.PHONY: full_lint
full_lint: $(VENV)
	$(PYTHON) -m pylint $(MODULES)

.PHONY: deep
deep:
	-$(RM) -r $(VENV)

.PHONY: clean
clean:
	-$(RM) -r $(CACHE)
	cd bin; ./clean.bash
	cd output; ./clean.bash
