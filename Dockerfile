FROM python:3.10

RUN useradd -ms /bin/sh -u 1001 app

ARG GITHUB_TOKEN
ENV GITHUB_TOKEN=${GITHUB_TOKEN}

WORKDIR /
COPY requirements.txt ./
RUN git config --global url."https://${GITHUB_TOKEN}@github.com/".insteadOf "https://github.com/" && \
    pip install --no-cache-dir --upgrade -r requirements.txt && \
    git config --global --unset url."https://${GITHUB_TOKEN}@github.com/".insteadOf

COPY --chown=app:app ./app /app

USER app

CMD uvicorn app.main:app --host 0.0.0.0 --port 80 --reload