#!/usr/bin/env bash

# envファイルが存在するか確認
if [ ! -e stg.env ]; then
  echo ".env does not exist."
  exit 1
fi

# 起動ずみのコンテナを停止
docker stop jcw-demo-app-stg

# Dockerビルド
docker build -t jcw-demo:0.0.1 .

# アプリ起動
docker run --name jcw-demo-app-stg --rm -d -p 81:5000 \
--env-file .env \
jcw-demo:0.0.1
