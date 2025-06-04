# Inspired by https://postd.cc/auto-documented-makefile/
MAKEFLAGS += --warn-undefined-variables
SHELL = /bin/bash
.SHELLFLAGS = -e -o pipefail -c
.DEFAULT_GOAL = help

# Use UTF-8 as Python default encoding
export PYTHONUTF8 = 1

# If SHLVL is undefined, use bash in "Git for Windows"
ifndef SHLVL
    SHELL = C:\Program Files\Git\bin\bash.exe
endif

# Make all targets PHONY other than targets including . in its name
.PHONY: $(shell grep -oE ^[a-zA-Z0-9%_-]+: $(MAKEFILE_LIST) | sed 's/://')

# Tasks
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = make":.*?## "} /^[a-zA-Z0-9%_-]+:.*?## / {printf "    \033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)


lint: pinact actionlint ghqlint zizmor ## Run all linters

pinact: ## Lint by pinact
	@pinact run --check
	@pinact run --verify

actionlint: ## Lint by actionlint
	@actionlint

ghqlint: ## Lint by ghqlint
	@ghalint run

zizmor: ## Lint by zizmor
	@zizmor .github/workflows/
