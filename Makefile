STACK_NAME:= $(notdir $(CURDIR))

export BASE_IMAGE:=local/mini-osparc
export UID:=$(shell id -u)
export GID:=$(shell id -g)


help: ## help on rule's targets
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)



# docker-compose
docker-compose.yml:
	@python scripts/create-compose-file.py > $@

.PHONY: compose-dev.yml
compose-dev.yml:
	@docker-compose -f docker-compose.yml -f docker-compose-ops.yml config >$@



.PHONY: build
build: ## build IMAGES
	@docker build --file Dockerfile --tag   .

.PHONY: up
up: compose-dev.yml ## starts CONTAINERS
	@docker-compose --file $< up

.PHONY: down
down: compose-dev.yml ## stops CONTAINERS
	@docker-compose --file $< down



# docker-swarm
.PHONY: init
init: ## inits SWARM
	docker swarm init

.PHONY: deploy
deploy: compose-dev.yml ## deploy/update stack in SWARM
	docker stack deploy --with-registry-auth --compose-file $< ${STACK_NAME}
	@echo ''make remove'' to stop swarm

.PHON: remove
remove: ## remove stack from SWARM
	docker stack rm ${STACK_NAME}

.PHONY: leave
leave: ## leaves SWARM
	docker swarm leave --force



# in-place development
# TODO: devcontainer?

.venv:
	python3 -m venv $@
	$@/bin/pip3 --quiet install --upgrade \
		pip \
		wheel \
		setuptools
	@echo "To activate the venv, execute 'source .venv/bin/activate'"


.PHONY: dev-env
env-dev: ## env-devel
	pip install -r requirements-dev.txt
	pre-commit install



.PHONY: info
info: ## environment info
	@python --version
	@pip --version
	@pip list
	@echo ---
	@printenv


.PHONY: clean
clean: ## clean except if 'keep' in name
	git clean -dxf --exclude=*keep*
