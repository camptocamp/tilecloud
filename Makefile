export DOCKER_BUILDKIT = 1
DOCKER_BUILD_ARG = $(shell bash -c '[ "$$CI" == "true" ] && echo "--pull"')

.PHONY: help
help: ## Display this help message
	@echo "Usage: make <target>"
	@echo
	@echo "Available targets:"
	@grep --extended-regexp --no-filename '^[a-zA-Z_-]+:.*## ' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "	%-20s%s\n", $$1, $$2}'

.PHONY: all
all: tests prospector docs

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f
	make -C docs clean

.PHONY: docs
docs: ## Make the documentation
	make -C docs html


.PHONY: prospector
prospector:
	prospector --output=pylint --die-on-tool-error

.PHONY: tests
tests:
	pytest --verbose --color=yes --cov=tilecloud

.PHONY: build ## build the images for the checks
build:
	docker-compose build $(DOCKER_BUILD_ARG)

.PHONY: checks ## Run the checks
checks: build
	docker-compose up --exit-code-from test
