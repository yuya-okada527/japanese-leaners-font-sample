#!/usr/bin/env bash

if [ ! -e .env ]; then
  echo ".env does not exist."
  exit 1
fi

# 起動ずみのコンテナを停止
# docker stop jcw-demo-log
docker stop jcw-demo-app

# Dockerビルド
# docker build -t jcw-demo-log:0.0.1 logs/
docker build -t jcw-demo:0.0.1 .

# 81ポートにルーティング
docker run --name jcw-demo-app --rm -d -p 81:5000 \
--env-file .env \
jcw-demo:0.0.1
