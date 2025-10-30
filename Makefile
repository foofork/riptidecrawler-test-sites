# Makefile for RipTide Test Sites
.PHONY: help build up down restart health-check test test-fast test-slow test-phase1 test-phase2 validate ground-truth clean logs

PYTHON := python3
PYTEST := pytest
DOCKER_COMPOSE := docker-compose

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help:
	@echo '${GREEN}RipTide Test Sites - Make Commands${RESET}'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  ${YELLOW}%-20s${RESET} %s\n", $$1, $$2}' $(MAKEFILE_LIST)

build: ## Build Docker services
	$(DOCKER_COMPOSE) build

up: ## Start all services
	$(DOCKER_COMPOSE) up -d
	@./scripts/health_check_new.sh --wait

down: ## Stop all services
	$(DOCKER_COMPOSE) down

test: up ## Run all tests
	$(PYTEST) tests/ -v --tb=short

test-phase1: up ## Run Phase 1 tests
	$(PYTEST) tests/ -v --tb=short -m phase1

test-phase2: up ## Run Phase 2 tests
	$(PYTEST) tests/ -v --tb=short -m phase2

validate: ## Validate fixtures
	@$(PYTHON) scripts/validate_fixtures.py --all

ground-truth: up ## Generate ground truth
	@$(PYTHON) scripts/generate_ground_truth.py --all --validate --include-sitemap

clean: down ## Clean up
	$(DOCKER_COMPOSE) down -v --remove-orphans
	@rm -rf htmlcov/ .pytest_cache/ tests/__pycache__/

.DEFAULT_GOAL := help
