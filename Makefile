.PHONY: all help setup test verification lint format typecheck test-cov secret-scan dep-audit \
        lockfile health-check docker-up docker-down db-up db-down compose build-phase3

all: help ## Display help message

help: ## Display help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' Makefile | sort | column -t -s ':' -n 2

setup: ## Initialize project structure and verify prerequisites
	@uv run --no-sync nox -s setup

test: ## Run all required checks (the local verification lane)
	@uv run --no-sync nox -s fast_checks

verification: test ## Alias for the local verification lane

lint: ## Run linting only
	@uv run --no-sync nox -s lint

format: ## Run formatting only
	@uv run --no-sync nox -s format

typecheck: ## Run type checking only
	@uv run --no-sync nox -s typecheck

test-cov: ## Run tests with coverage
	@uv run --no-sync nox -s test_cov

secret-scan: ## Run secret scanning
	@uv run --no-sync nox -s secret_scan

dep-audit: ## Run dependency audit
	@uv run --no-sync nox -s dep_audit

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

build-phase3: ## Run build-phase3 specific checks
	@uv run --no-sync nox -s run_build_phase3 || true
