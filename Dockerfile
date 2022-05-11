ARG PYTHON_VERSION="3.10.0"
FROM python:${PYTHON_VERSION}-slim-buster as base

RUN apt-get update; apt-get install -y curl


COPY requirements.txt requirements.txt
RUN pip install --upgrade pip wheel setuptools \
    pip install -r requirements.txt
