.PHONY: all
all: test pep8 pyflakes docs

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f
	make -C docs clean

.PHONY: docs
docs:
	make -C docs html

.PHONY: pep8
pep8:
	find examples tilecloud tiles -name \*.py | xargs pep8 --ignore=E501,W503,E203
	pep8 --ignore=E501 tc-*

.PHONY: pyflakes
pyflakes:
	find examples tilecloud tiles -name \*.py | xargs pyflakes
	pyflakes tc-*

.PHONY: test
test:
	pytest -vv --cov=tilecloud

.PHONY: pypi-upload
pypi-upload: test pep8
	python setup.py sdist upload

.venv/timestamp: requirements.txt dev-requirements.txt Makefile
	/usr/bin/virtualenv --python=/usr/bin/python3 .venv
	.venv/bin/pip install --upgrade -r requirements.txt -r dev-requirements.txt
	touch $@
	@echo "Type in your shell: source .venv/bin/activate"
