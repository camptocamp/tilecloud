.PHONY: all
all:

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f

.PHONY: pep8
pep8:
	find tilecloud tiles bin -name \*.py | xargs pep8.py
	pep8.py tc-*

.PHONY: pyflakes
pyflakes:
	find tilecloud tiles bin -name \*.py | xargs pyflakes
	pyflakes tc-*
