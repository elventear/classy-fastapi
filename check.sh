#!/bin/bash

# Simple shell script to run unit tests, MyPy and flake8

poetry install
poetry run pytest
poetry run mypy -p classy_fastapi
poetry run flake8
