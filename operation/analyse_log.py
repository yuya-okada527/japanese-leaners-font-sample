import os
import sys
import json
import time
from pathlib import Path
from enum import Enum
from typing import List, Dict, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
DATE_KEY_FMT = "%Y/%m/%d"


class AccessRoute(Enum):
    DEFAULT = (
        "/",
        os.path.join(
            Path(__file__).resolve().parents[0],
            "logs",
            "default.tsv"
        )
    )
    CREATE = (
        "/create",
        os.path.join(
            Path(__file__).resolve().parents[0],
            "logs",
            "create.tsv"
        )
    )
    DOWNLOAD = (
        "/download",
        os.path.join(
            Path(__file__).resolve().parents[0],
            "logs",
            "download.tsv"
        )
    )

    def __new__(
            cls,
            route: str,
            log_path: Callable
    ):
        obj = object.__new__(cls)
        obj._value_ = route
        obj.log_path = log_path

        return obj


@dataclass()
class AccessLog:
    date_time: datetime
    ip_address: str
    method: str
    route: str
    queries: Dict[str, str]
    status_code: int


def calc_time(sec):
    hour, res = divmod(sec, 60**2)
    minutes, second = divmod(res, 60)
    return hour, minutes, second


def parse_query(query_string: str) -> Dict[str, str]:
    return json.loads(query_string)


def parse_log_string(log_string: str) -> AccessLog:
    log = log_string.strip().split("\t")
    if len(log) != 6:
        raise ValueError(f"log size is invalid: size={len(log)}, log={log}")

    return AccessLog(
        date_time=datetime.strptime(log[0], DATETIME_FMT) + timedelta(hours=9),
        ip_address=log[1],
        method=log[2],
        route=log[3],
        queries=parse_query(log[4]),
        status_code=int(log[5])
    )


def download_logs(log_path: str) -> List[AccessLog]:
    with open(log_path, mode="r", encoding="utf-8") as f:
        access_logs = []
        for i, log in enumerate(f):
            if i == 0:
                continue
            access_logs.append(parse_log_string(log))
        return access_logs


def count_user(access_logs: List[AccessLog]) -> int:
    return len(set([access_log.ip_address for access_log in access_logs]))


def analyse_default_route():
    print("Start analysing default route /")


def analyse_create_route():
    print("Start analysing create route /create")

    # アクセスログを取得
    access_logs = download_logs(AccessRoute.CREATE.log_path)

    # クエリごとにログを集計
    texts = set()
    sizes = defaultdict(int)
    horizontals = 0
    for log in access_logs:
        texts.add(log.queries.get("text", None))
        sizes[log.queries.get("font-size", None)] += 1
        horizontals += bool(log.queries.get("horizontal", "0"))

    # 集計結果を出力
    print(f"/create リクエスト数: {len(access_logs)}")
    for text in texts:
        print(f"{text}")
    for size, count in sizes.items():
        print(f"{size} = {count}")
    print(f"横: {horizontals}, 縦: {len(access_logs) - horizontals}")


def analyse_download_route():
    print("Start analysing download route /download")

    # アクセスログを取得
    access_logs = download_logs(AccessRoute.DOWNLOAD.log_path)

    # ダウンロードファイルごとに数を集計
    files =defaultdict(int)
    for log in access_logs:
        files[log.queries.get("key")] += 1

    # 集計結果を出力
    print(f"/download リクエスト数: {len(access_logs)}")
    for file, count in files.items():
        print(f"file={file} is downloaded {count} times")


def analyse_all_route():
    print("Start analysing all route ['/', '/create', '/download']")

    # アクセスログを全て取得
    access_logs = []
    access_logs.extend(download_logs(AccessRoute.DEFAULT.log_path))
    access_logs.extend(download_logs(AccessRoute.CREATE.log_path))
    access_logs.extend(download_logs(AccessRoute.DOWNLOAD.log_path))

    # アクセス数を計算
    access_count = len(access_logs)
    user_count = count_user(access_logs)
    print(f"総アクセス数: {access_count}, 総ユーザ数: {user_count}")

    # 日にちごとのアクセス数を計算
    access_by_day = defaultdict(list)
    for access_log in access_logs:
        day = access_log.date_time.strftime(DATE_KEY_FMT)
        access_by_day[day].append(access_log)

    for day, logs in access_by_day.items():
        print(f"{day}: 総アクセス: {len(logs)}, 総ユーザ数: {count_user(logs)}")


class ServiceDiv(Enum):
    DEFAULT = (
        "default",
        analyse_default_route
    )
    CREATE = (
        "create",
        analyse_create_route
    )
    DOWNLOAD = (
        "download",
        analyse_download_route
    )
    ALL = (
        "all",
        analyse_all_route
    )

    def __new__(
            cls,
            value: str,
            service: Callable
    ):
        obj = object.__new__(cls)
        obj._value_ = value
        obj.service = service

        return obj

    @classmethod
    def value_of(cls, value: str):
        for e in cls:
            if e.value == value:
                return e
        raise ValueError(f"{value} is not valid route.")


def main(target):

    # 解析対象のルートを取得
    try:
        target_service = ServiceDiv.value_of(target)
    except ValueError as e:
        print(e)
        exit(1)

    # 開始時刻を記録
    start = time.time()

    # 解析サービスを実行
    try:
        target_service.service()
    except Exception as e:
        raise e
        # exit(1)

    # 終了処理
    end = time.time()
    hour, minutes, sec = calc_time(end - start)
    print(f"process time is {hour}h {minutes}m {sec}s")
    print("Finished analysis")
    exit(0)


if __name__ == "__main__":
    main(sys.argv[1])
