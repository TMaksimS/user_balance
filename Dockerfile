FROM python:3.12-slim
RUN apt-get update && apt-get install curl --yes
COPY poetry.lock pyproject.toml ./
RUN pip install --upgrade pip
RUN pip install poetry
RUN poetry install --no-root
COPY . .
RUN rm -rf .venv
WORKDIR .