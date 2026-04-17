#!/usr/bin/env make

.PHONY: build run run-bg utest itest test

build:
	docker build -t score-service:latest .

run:
	docker run --network=host --env-file=.env -it score-service:latest

run-bg:
	docker run --network=host --env-file=.env -d score-service:latest

utest:
	pytest

itest:
	docker compose -f docker-compose.test.yml up -d --wait
	pytest -m integration tests/integration

test: utest itest
