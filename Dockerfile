# ==============================================================================
# Dockerfile - Docker Container Configuration
# ==============================================================================
# This file defines the Docker container setup for HasiiMusicBot.
# 
# Base Image: Python 3.13 slim (minimal Python installation)
# 
# Installed Dependencies:
# - FFmpeg: Required for audio/video processing
# - Deno: JavaScript/TypeScript runtime (used for certain features)
# - Python packages from requirements.txt
# 
# Usage:
#   docker build -t hasii-music-bot .
#   docker run -d --env-file .env hasii-music-bot
# ==============================================================================

FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get update -y && apt-get upgrade -y \
    && apt-get install -y --no-install-recommends ffmpeg curl unzip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deno.land/install.sh | sh \
    && ln -s /root/.deno/bin/deno /usr/local/bin/deno

RUN pip3 install -U pip && pip3 install -U -r requirements.txt
COPY . .

CMD ["bash", "start"]
