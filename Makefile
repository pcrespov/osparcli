STACK_NAME:= $(notdir $(CURDIR))
export UID:=$(shell id -u)
export GID:=$(shell id -g)


# docker-compose

.PHONY: compose-dev.yml
compose-dev.yml:
	@docker-compose -f docker-compose.yml -f docker-compose-ops.yml config >$@

.PHONY: build
build:
	@docker-compose build

.PHONY: up
up: compose-dev.yml
	@docker-compose --file $< up

.PHONY: down
down: compose-dev.yml
	@docker-compose --file $< down



# docker-swarm
.PHONY: init
init:
	docker swarm init

.PHONY: deploy
deploy: compose-dev.yml
	docker stack deploy --with-registry-auth --compose-file $< ${STACK_NAME}

.PHON: remove
remove:
	docker stack rm ${STACK_NAME}

.PHONY: leave
leave:
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
env-dev:
	pip install -r requirements-dev.txt


.PHONY: info
info:
	@python --version
	@pip --version
	@pip list


.PHONY: clean
clean:
	git clean -dxf --exclude=*keep*
