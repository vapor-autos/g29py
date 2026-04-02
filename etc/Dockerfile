# from ubuntu 24.04
FROM ubuntu:noble

WORKDIR /app

# dependencies
RUN apt-get -y update
RUN apt-get update && apt-get install -y \
    curl \
    git \
    pipx \
    python3 \
    python3-pip \
    python3-full \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# install poetry
RUN pipx install poetry

# add $HOME/.local/bin to path
ENV PATH="$PATH:/root/.local/bin"
RUN poetry --version

COPY pyproject.toml poetry.lock README.md ./
COPY g29py ./g29py

RUN poetry build && poetry install
