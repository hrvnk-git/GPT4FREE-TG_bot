# syntax=docker/dockerfile:1
FROM python:3.13-slim
USER root
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y \
    ffmpeg \
    flack \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]