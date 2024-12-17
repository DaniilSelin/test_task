FROM ubuntu:latest
LABEL authors="DaniilSelin)"

WORKDIR /eKom

COPY . /eKom

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    wget \
    curl \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-dev


RUN python3 -m venv venv

RUN . venv/bin/activate && pip install --no-cache-dir -r requirements.txt
EXPOSE 5000

RUN . venv/bin/activate && flask run