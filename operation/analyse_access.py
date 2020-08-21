import os
import re
import json
from pathlib import Path
import gzip
from io import BytesIO
from dataclasses import dataclass
from typing import Dict, Tuple

from dotenv import load_dotenv
from boto3.session import Session

ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[0],
    ".env"
)

LOG_PREFIX = "logs/"
LOG_PATTERN = r"^(.+) - - .+\".*(GET|POST) (/.*) HTTP.+\" ([0-9]+) -.*$"


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


def parse_request(req_str: str) -> Tuple[str, Dict[str, str]]:
    request = req_str.split("?")
    if len(request) == 1:
        return request[0], {}

    route = request[0]
    query_str = request[1]

    queries = {}
    for query in query_str.split("&"):
        key, value = split_query(query)
        queries[key] = value

    return route, queries


def split_query(query):
    if len(query.split("=")) == 2:
        return query.split("=")
    return query, ""


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
        # print(message)
        # TODO ANSI Color Code Remove
        m = re.match(LOG_PATTERN, message)
        if m:
            route, queries = parse_request(m.group(3))
            access_log = AccessLog(
                date_time=date_time,
                ip_address=m.group(1),
                method=m.group(2),
                route=route,
                queries=queries,
                status_code=m.group(4)
            )
            print(access_log)

            access_logs.append(access_log)


if __name__ == "__main__":
    main()
