# syntax=docker/dockerfile:1
FROM python:3.13-alpine
USER root
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python3", "main.py"]