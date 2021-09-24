ARG PYTHON_VERSION="3.8.10"
FROM python:${PYTHON_VERSION}-slim-buster as base

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip wheel setuptools \
    pip install -r requirements.txt
