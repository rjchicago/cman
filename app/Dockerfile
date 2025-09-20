FROM python:3.11-slim

WORKDIR /app

COPY src ./src
COPY levels ./levels

WORKDIR /app/src

CMD ["python3", "cman.py"]