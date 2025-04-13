# syntax=docker/dockerfile:1

FROM python:3.13-slim as builder
WORKDIR /app

### Финальный образ с минимальной сборкой ffmpeg и утилитой flac
FROM python:3.13-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY --from=builder /app /app

# Устанавливаем wget и xz-utils для работы с xz-архивами и скачивания ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends wget xz-utils flac \
    && wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar -xJf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*-static/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*-static/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-*-static ffmpeg-release-amd64-static.tar.xz \
    && apt-get purge -y wget xz-utils && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
RUN pip install uv
COPY . /app
CMD ["uv", "run", "main.py"]