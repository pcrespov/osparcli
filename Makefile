export UID:=$(shell id -u)
export GID:=$(shell id -g)

.venv:
	python3 -m venv $@
	$@/bin/pip3 --quiet install --upgrade \
		pip \
		wheel \
		setuptools
	@echo "To activate the venv, execute 'source .venv/bin/activate'"

.PHONY: config
config:
	@docker-compose config

.PHONY: build
build:
	@docker-compose build

.PHONY: up
up:
	@docker-compose up

.PHONY: down
down:
	@docker-compose down

