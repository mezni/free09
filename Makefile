.PHONY: all help setup test lint format typecheck test-cov secret-scan dep-audit docker-up docker-down compose

all: help ## Display help

help: ## Display help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | column -t -s ':' -n 2

setup: ## Initialize project structure (run nox -l setup)
	@nox -l setup || true

test: ## Run all required checks
	@nox run fast-checks

lint: ## Run linting only
	@nox run format

typecheck: ## Run type checking only
	@nox run typecheck

format: ## Run formatting only
	@nox run ruff check --select I

test-cov: ## Run tests with coverage
	@nox run test

secret-scan: ## Run secret scanning
	@nox run secret-scan

dep-audit: ## Run dependency audit
	@nox run dep-audit

docker-up: ## Start docker compose
	@docker compose -f deploy/compose/compose.yaml up -d

docker-down: ## Stop docker compose
	@docker compose -f deploy/compose/compose.yaml down

.PHONY: setup db-up db-down

setup: ## Initialize project structure and verify prerequisites
	@nox -l setup

db-up: ## Start PostgreSQL via docker compose
	@docker compose -f deploy/compose/compose.yaml up -d postgres

db-down: ## Stop PostgreSQL via docker compose
	@docker compose -f deploy/compose/compose.yaml down
