.PHONY: all help setup test verify verification test test-cov lint format typecheck \
        secret-scan dependency-audit governance file-coverage lockfile health-check \
        docker-up docker-down db-up db-down

all: help ## Display help message

help: ## Display help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | column -t -s ':' -n 2

setup: ## Initialize project structure and verify prerequisites
	@uv run --no-sync nox -s setup

verify: ## Run every required check (the merge gate's local equivalent)
	@uv run --no-sync nox

test: ## Run the fast lane: exactly the checks the CI fast-checks job runs
	@uv run --no-sync nox -s fast_checks

verification: verify ## Alias for the full required-check run

lint: ## Run linting only
	@uv run --no-sync nox -s lint

format: ## Run formatting only
	@uv run --no-sync nox -s format

typecheck: ## Run type checking only
	@uv run --no-sync nox -s typecheck

test-cov: ## Run tests with coverage
	@uv run --no-sync nox -s test_cov

secret-scan: ## Scan the tree and the history for secrets
	@uv run --no-sync nox -s secret-scan

dependency-audit: ## Audit the locked dependency set against the advisory snapshot
	@uv run --no-sync nox -s dependency-audit

governance: ## Verify the governance artefacts
	@uv run --no-sync nox -s governance

file-coverage: ## Verify that every tracked file is covered by a required check
	@uv run --no-sync nox -s file-coverage

lockfile: ## Verify the lockfile is current
	@uv run --no-sync nox -s lockfile

health-check: ## Probe the local runtime health endpoint
	@uv run --no-sync nox -s health_check

docker-up: ## Start docker compose
	@docker compose -f deploy/compose/compose.yaml up -d

docker-down: ## Stop docker compose
	@docker compose -f deploy/compose/compose.yaml down

db-up: ## Start PostgreSQL via docker compose
	@docker compose -f deploy/compose/compose.yaml up -d postgres

db-down: ## Stop PostgreSQL via docker compose
	@docker compose -f deploy/compose/compose.yaml down
