.PHONY: all
all: test prospector docs

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f
	make -C docs clean

.PHONY: docs
docs:
	make -C docs html

.PHONY: prospector
prospector:
	prospector tilecloud

.PHONY: test
test:
	pytest -vv --cov=tilecloud

.PHONY: pypi-upload
pypi-upload: test prospector
	python3 setup.py sdist upload

.PHONY: checks
checks: prospector test
