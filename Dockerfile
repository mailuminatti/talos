FROM python:3.10-bullseye

WORKDIR /talos
RUN mkdir /app
RUN mkdir /app/cli

COPY requirements.txt /app
COPY meta.yaml /app

COPY cli/ /app/cli
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

RUN rm -rf __pycache__ && \
    rm -rf *.pyc && \
    rm -rf tests

RUN pip install  /app/cli
WORKDIR /talos
ENTRYPOINT ["/usr/local/bin/talos"]