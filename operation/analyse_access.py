import os
import re
import json
from pathlib import Path
import gzip
from io import BytesIO
from dataclasses import dataclass
from typing import Dict

from dotenv import load_dotenv
from boto3.session import Session

ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[0],
    ".env"
)

LOG_PREFIX = "logs/"


@dataclass()
class AccessLog:
    date_time: str
    ip_address: str
    method: str
    route: str
    queries: Dict[str, str]
    status_code: int


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
    logs = {}
    for log_str in log_texts:
        m = re.match(r"^(.*)\tdocker\.jcw-demo-app\t(.*)$", log_str)
        if m:
            logs[m.group(1)] = json.loads(m.group(2))["log"]

    # ログの解析
    access_logs = []
    for date_time, message in logs.items():
        # TODO ANSI Color Code Remove
        message = re.sub(r"\\x1b\[", "", message)
        m = re.match(r"^.+ - - \" ", message)
        if m:
            access_logs.append(AccessLog(
                date_time=date_time
            ))


if __name__ == "__main__":
    main()
