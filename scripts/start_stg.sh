#!/usr/bin/env bash

# envファイルが存在するか確認
if [ ! -e .env ]; then
  echo ".env does not exist."
  exit 1
fi

# 起動ずみのコンテナを停止
docker stop jcw-demo-app

# Dockerビルド
docker build -t jcw-demo-stg:0.0.1 .

# アプリ起動
docker run --name jcw-demo-app --rm -d -p 80:5000 \
--env-file .env \
jcw-demo-stg:0.0.1