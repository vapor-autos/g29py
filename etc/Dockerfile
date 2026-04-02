# from ubuntu 24.04
FROM ubuntu:noble

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

# install g29
RUN git clone git@github.com:vapor-autos/g29py.git && \
    cd g29-py && \
    poetry build && \
    poetry install
