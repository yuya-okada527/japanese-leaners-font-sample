#!/usr/bin/env bash

# 起動ずみのコンテナを停止
docker stop jcw-demo-app

# Dockerビルド
docker build -t jcw-demo:0.0.1 .

# アプリ起動
docker run -d --rm --name jcw-demo-app --env-file .env -p 80:5000 jcw-demo:0.0.1
