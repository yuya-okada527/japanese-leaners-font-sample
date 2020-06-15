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
- データストア -> S3
  - DBは諸々のコストがかかるし、必要ない気がする
  - バケットは、privateとpublicの2つ
    - private: フォントやログ出力用
      - パス
        - /fonts
        - /logs
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
- CI/CD
  - レポジトリ -> GitHub
    - とりあえず、publicリポジトリで作った
    - 場所移すかも？
  - CI -> CodeBuild?
  - CD -> CodePipeline?
- フレームワーク
  - FE -> HTML(jinja2) + Bootstrap
  - BE -> Responder

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

