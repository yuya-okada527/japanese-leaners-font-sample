# japanese-leaners-font-sample

### 概要
日本語練習プリント作成サイトのサンプル

### 機能要件
- ユーザによって入力された文字列に対して、日本語練習プリントを作成する
  - 日本語練習プリントはPDFで出力されるものとする
  - 練習素材は、JapaneseLearnersFontを使用して作成する
- 静的ファイルとして、練習用のテキストを配布できる

### 非機能要件
- 運用
  - 非エンジニアで運用できる(ある程度は覚えてもらう)
    - 静的ファイルくらいは触れるようになってもらう
    - GitHubやマネージメントコンソールからの操作で済むくらい
- セキュリティ
  - フォントの元データは、外部ユーザがアクセスできないようにする
- コスト
  - なるべく安く

### タスク一覧
- インフラ設計
- データ設計
- 画面設計
- 環境構築
- FE実装
- BE実装
- インフラ構築
- デプロイ
- CI/CD作成

### インフラ設計
- インフラ -> AWS
- 実行基盤 -> ? (PaaSがいいけど)
  - Elastic Beanstalk
  - ECS
  - Lambda
    - 価格的には、Lambdaで行きたいかも
  - デモは、Elastic Beanstalkで、本番作るなら、Lambdaに作り直す
- データストア -> S3
  - DBは諸々のコストがかかるし、必要ない気がする
  - バケットは、privateとpublicの2つ
    - private: フォントやログ出力用
      - パス
        - /fonts
        - /fonts/ots
        - /fonts/tts
        - /logs
      - otsとttsはディレクトリ分ける
    - public: 画像や練習用テキストなどの静的ファイル用
      - パス
        - /images
        - /materials
    - publicの方は、CloudFrontを通して、外部に配布する
- ネットワーク
  - 冗長化等は行わない
  - ロードバランサいらない
  - HTTPS対応は、ひとまず後回し
  - ドメインはできれば取得したい？
  - VPC
    - インターネットゲートウェイは必要
    - publicサブネットを一つ切っておくくらいでいい気がする
    - LambdaならVPCは考えなくていい
- CI/CD
  - レポジトリ -> GitHub
    - とりあえず、publicリポジトリで作った
    - 場所移すかも？
  - CI -> CodeBuild?
  - CD -> CodePipeline?
  - CI/CDは、CircleCI -> Elastic Beanstalkを検討
    - この場合、フレームワークはFlask前提となる
  - デモではCI/CDまでは作らない
- フレームワーク
  - FE -> HTML(jinja2) + Bootstrap
  - BE -> Responder or Flask
  - ランタイム -> Pythonなるべく新しいの使いたいけど実行環境依存
  - Lambdaなら、Zappa + Flask or SPAでBEはPure Python
    - SPAだと、JSが技術スタックに入るのが考えもん
  - デモは、さっくり適当に作る
    - FlaskでPython3.7
- PDF操作ライブラリ
  - ReportLabが良さそう
    - ただ、フォントがTTFの必要があるみたいだから、ttfで用意できないか聞いてみる
      - TTFフォントの用意は無理そう
      - OTFからTTFに変換するコマンドラインツールを利用する
        - https://pypi.org/project/otf2ttf/
      - 余裕があれば、Lambdaに変換ツール作って、S3へのアップロードをトリガーにして、変換すバッチを仕込む

### 画面設計
- 画面一覧
  - 目次
    - HTML: index.html
    - Path: /
  - 教材
    - HTML: materials.html
    - Path: /materials
  - 教材作成
    - HTML: create.html
    - Path: /create
    
### 起動方法
```bash
$ python -m web.main

```

