# japanese-leaners-font-sample

### 概要

日本語練習プリント作成サイトのサンプル

### 起動方法

```bash
# WEBアプリローカルでの起動方法
$ python -m web.main

# コンテナビルド
$ docker build -t jcw-demo:0.0.1 .

# コンテナ起動
$ docker run --rm --name jcw-demo-app --env-file .env -p 5000:5000 jcw-demo:0.0.1

# プッシュ
$ aws ecr get-login --no-include-email | sh
$ docker tag jcw-demo:latest {AWSAccount}.dkr.ecr.ap-northeast-1.amazonaws.com/ujiie/jcw-demo-app:latest
$ docker push {AWSAccount}.dkr.ecr.ap-northeast-1.amazonaws.com/ujiie/jcw-demo-app:latest

# OTFからTTFへの変換(結構時間かかる)
$ otf2ttf ./fonts/ttf/JapaneseLearners1.otf
```

### サーバー起動手順

```bash
# サーバーの準備を整える
$ sh scripts/init.sh

# .envファイルの作成
$ vi .env

# 一度抜ける
$ exit

# アプリを起動
$ sh scripts/start.sh

# STGアプリを起動
$ sh scripts/start_stg.sh

```
