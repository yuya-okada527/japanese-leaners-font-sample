#!/usr/bin/env bash

# envファイルが存在するか確認
if [ ! -e logs/.env ]; then
  echo "logs/.env does not exist."
  exit 1
fi

if [ ! -e .env ]; then
  echo ".env does not exist."
  exit 1
fi

# 起動ずみのコンテナを停止
docker stop jcw-demo-log
docker stop jcw-demo-app

# Dockerビルド
docker build -t jcw-demo-log:0.0.1 logs/
docker build -t jcw-demo:0.0.1 .

# アプリ起動
docker run --name jcw-demo-log --rm -d -p 8888:8888  \
--env-file logs/.env \
jcw-demo-log:0.0.1

docker run --name jcw-demo-app --rm -d -p 80:5000 \
--env-file .env \
--log-driver=fluentd \
--log-opt fluentd-address=localhost:8888 \
--log-opt tag=docker.{{.Name}} \
jcw-demo:0.0.1
