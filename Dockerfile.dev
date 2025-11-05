FROM python:3.10

RUN useradd -ms /bin/sh -u 1001 app

WORKDIR /
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=app:app ./app /app

USER app

CMD uvicorn app.main:app --host 0.0.0.0 --port 80 --reload