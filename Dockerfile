ARG PYTHON_VERSION=3.11

FROM python:$PYTHON_VERSION-slim

USER root

RUN apt-get update \
    && apt-get install --no-install-recommends -y sudo gcc g++ \
    &&  useradd -m -r -G root --shell /usr/bin/bash me \
    && rm -rf /var/lib/apt/lists/*

USER me

WORKDIR /app

ENV HOME=/home/me
ENV PATH="${HOME}/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH="/app/src:$PYTHONPATH"

ADD requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --user -U pip  \
    && pip install --no-cache-dir --user  -r /app/requirements.txt

COPY src .
COPY scripts/generator.py /app/bin/entrypoint

CMD [ "/entrypoint","-help" ]