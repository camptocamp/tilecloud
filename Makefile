.PHONY: checks
checks:
	docker-compose build
	docker-compose up --exit-code-from tests

.PHONY: tests-fast
tests-fast:
	docker-compose build
	docker-compose up --exit-code-from tests

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f
	make -C docs clean

.PHONY: docs
docs:
	make -C docs html

.PHONY: prospector
prospector:
	prospector tilecloud --output=pylint

.PHONY: tests
tests:
	pytest -vv --cov=tilecloud

.PHONY: checks-internal
checks-internal: prospector tests
