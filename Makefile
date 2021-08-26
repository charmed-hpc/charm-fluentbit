# Display target comments in 'make help'
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: lint
lint: ## Run linter
	flake8 src/

.PHONY: version
version: ## Create/update version file
	@git describe --dirty --tags > version

.PHONY: clean
clean: ## Remove build dirs, temp files, and charms
	rm -rf venv/
	find . -name "*.charm" -delete
	rm -rf build
	rm -rf version

.PHONY: charm
charm: version ## Pack the charm
	@charmcraft pack
