#!/usr/bin/env bash

# パッケージを最新化
sudo yum update -y

# gitのインストール
sudo yum install -y git

# リポジトリのクローン
git clone https://github.com/yuya-okada527/japanese-leaners-font-sample.git
cd japanese-leaners-font-sample

# dockerの準備
sudo amazon-linux-extras install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user
