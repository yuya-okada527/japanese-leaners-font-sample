import os
import re
import json
from pathlib import Path
import gzip
from io import BytesIO

from dotenv import load_dotenv
from boto3.session import Session

ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[0],
    ".env"
)

LOG_PREFIX = "logs/"


def decompress(file_obj):
    with gzip.open(BytesIO(file_obj), mode="rt") as f:
        try:
            return f.read()
        except UnicodeDecodeError as e:
            return ""


def main():

    # 環境変数を読み込み
    load_dotenv(ENV_FILE, verbose=True)

    # ログファイルを取得
    session = Session(
        aws_access_key_id=os.getenv("S3_USER_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("S3_USER_SECRET_KEY")
    )
    bucket = session.resource("s3").Bucket(os.getenv("S3_BUCKET_NAME"))
    log_texts = []
    for log_text in bucket.objects.filter(Prefix=LOG_PREFIX):
        log_texts.extend(decompress(log_text.get()["Body"].read()).split("\n"))

    # ログデータのパース
    logs = []
    for log_str in log_texts:
        m = re.match(r"^.*docker\.jcw-demo-app\t(.*)$", log_str)
        if m:
            logs.append(json.loads(m.group(1))["log"])


    for log in logs:
        print(log)


if __name__ == "__main__":
    main()
