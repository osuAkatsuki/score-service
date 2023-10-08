#!/usr/bin/env make

build:
	docker build -t score-service:latest .

run:
	$(eval include .env)
	docker run --network=host --env-file=.env -it score-service:latest

run-bg:
	$(eval include .env)
	docker run --network=host --env-file=.env -d score-service:latest
