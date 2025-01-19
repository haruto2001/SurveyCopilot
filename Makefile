.PHONY: build run-cpu run-gpu chack format isort

IMAGE_NAME = "survey-copilot"

build:
	docker build . -t $(IMAGE_NAME)

run-cpu:
	docker run -it --rm \
	--env-file ./.env \
	--mount type=bind,src=./pyproject.toml,dst=/work/pyproject.toml \
	--mount type=bind,src=./uv.lock,dst=/work/uv.lock \
	--mount type=bind,src=./.python-version,dst=/work/.python-version \
	--mount type=bind,src=./data,dst=/work/data \
	--mount type=bind,src=./src,dst=/work/src \
	$(IMAGE_NAME) bash

check:
	uvx ruff check ./src

format:
	uvx ruff format --diff ./src

isort:
	uvx isort --diff ./src