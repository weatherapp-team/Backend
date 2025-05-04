FROM python:3-alpine3.21 AS build

RUN adduser --system --no-create-home fastapi

RUN apk add --no-cache curl=8.12.1-r1

HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost/ || exit 1

WORKDIR /app

COPY requirements.txt /app

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY src/ /app/src/

RUN mkdir -p /app/data && touch /app/data/weather.db && chown -R fastapi /app/data

USER fastapi

EXPOSE 5050/tcp

CMD ["fastapi", "run", "src/main.py", "--port", "5050"]