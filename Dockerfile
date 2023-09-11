FROM python:3.9-alpine

WORKDIR /app

COPY requirements.txt /app
COPY meta.yaml /app
COPY cli/ /app/cli

RUN pip install --no-cache-dir -r requirements.txt

RUN rm -rf __pycache__ && \
    rm -rf *.pyc && \
    rm -rf tests

RUN pip install --editable /app/cli
ENTRYPOINT ["/usr/local/bin/talos"]