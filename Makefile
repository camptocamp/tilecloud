.PHONY: all
all:

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f

.PHONY: pep8
pep8:
	find tilecloud tiles -name \*.py | xargs pep8 --ignore=E501
	pep8 --ignore=E501 tc-*

.PHONY: pyflakes
pyflakes:
	find tilecloud tiles -name \*.py | xargs pyflakes
	pyflakes tc-*

.PHONY: test
test:
	python setup.py nosetests
