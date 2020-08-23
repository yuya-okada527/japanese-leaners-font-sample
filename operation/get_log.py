import os
import re
import json
from pathlib import Path
import gzip
from io import BytesIO
from dataclasses import dataclass
from typing import List, Dict, Tuple, Any
from collections import defaultdict
import time

from dotenv import load_dotenv
from boto3.session import Session

ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[0],
    ".env"
)
CONFIG_PATH = os.path.join(
    Path(__file__).resolve().parents[0],
    "config.json"
)
LOG_DIR = os.path.join(
    Path(__file__).resolve().parents[0],
    "logs"
)
LOG_EXTENSION = ".tsv"

LOG_PREFIX = "logs/"
LOG_PATTERN = r"^(.+) - - .+\".*(GET|POST) (/.*) HTTP.+\" ([0-9]+) -.*$"
LOG_TSV_HEADER = "DATE_TIME(UTF)\tIP_ADDRESS\tMETHOD\tROUTE\tQUERIES\tSTATUS_CODE\n"


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


def calc_time(sec):
    hour, res = divmod(sec, 60**2)
    minutes, second = divmod(res, 60)
    return hour, minutes, second


def get_config(file_path: str) -> Dict[str, Any]:
    with open(file_path, mode="r", encoding="utf-8") as f:
        return json.load(f)


def update_config(config: Dict[str, Any], file_path: str) -> None:
    with open(file_path, mode="w", encoding="utf-8") as wf:
        wf.write(json.dumps(config))


def make_log_path(route: str, log_dir: str) -> str:
    file_name = make_file_name(route)
    return os.path.join(log_dir, file_name)


def make_file_name(route: str) -> str:
    if route == "/":
        return "default" + LOG_EXTENSION
    return route[1:].replace("/", "_") + LOG_EXTENSION


def save_logs(access_logs: List[AccessLog], log_path: str) -> None:
    # TSVファイルの書き込み
    # ヘッダーの書き込み
    if not os.path.exists(log_path):
        with open(log_path, mode="w", encoding="utf-8") as wf:
            wf.write(LOG_TSV_HEADER)

    # TSVデータの書き込み
    with open(log_path, mode="a", encoding="utf-8") as wf:
        for access_log in access_logs:
            date_time = access_log.date_time
            ip_address = access_log.ip_address
            method = access_log.method
            route = access_log.route
            queries = json.dumps(access_log.queries)
            status_code = access_log.status_code
            wf.write(f"{date_time}\t{ip_address}\t{method}\t{route}\t{queries}\t{status_code}\n")


def main():

    # 時間計測
    start = time.time()

    # 設定ファイルを取得
    config = get_config(CONFIG_PATH)

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
        if log_text.key <= config["last_processed_file"]:
            continue
        print(f"key={log_text.key} is processing...")
        log_texts.extend(decompress(log_text.get()["Body"].read()).split("\n"))

    # 設定ファイルを書き換え
    config["last_processed_file"] = log_text.key
    update_config(config, CONFIG_PATH)

    # ログデータのパース
    logs = {}
    for log_str in log_texts:
        m = re.match(r"^(.*)\tdocker\.jcw-demo-app\t(.*)$", log_str)
        if m:
            logs[m.group(1)] = json.loads(m.group(2))["log"]

    # ログの解析
    access_logs = defaultdict(list)
    for date_time, message in logs.items():
        m = re.match(LOG_PATTERN, message)
        if m:
            # route+queryの解析
            route, queries = parse_request(m.group(3))
            access_log = AccessLog(
                date_time=date_time,
                ip_address=m.group(1),
                method=m.group(2),
                route=route,
                queries=queries,
                status_code=m.group(4)
            )

            # ルートごとに保持する
            access_logs[route].append(access_log)

    # ルートごとにlogファイルを作成する
    for route, access_log_list in access_logs.items():
        log_path = make_log_path(route, LOG_DIR)
        save_logs(access_log_list, log_path)

    # 時間計測
    end = time.time()
    hour, minutes, sec = calc_time(end - start)
    print(f"process time is {hour}h {minutes}m {sec}s")


if __name__ == "__main__":
    main()
