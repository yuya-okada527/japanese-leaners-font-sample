import os
import sys
import json
import time
from pathlib import Path
from enum import Enum
from typing import List, Dict, Callable, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

from jinja2 import Environment, FileSystemLoader

DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
DATE_KEY_FMT = "%Y/%m/%d"

ANALYSIS_TEXT = os.path.join(
    Path(__file__).resolve().parents[0],
    "analysis",
    "text.txt"
)
TEMPLATE_DIR = os.path.join(
    Path(__file__).resolve().parents[0],
    "template"
)
OUTPUT_HTML = "access_analysis.html"
RENDERED_HTML_PATH = os.path.join(
    Path(__file__).resolve().parents[0],
    "rendered",
    OUTPUT_HTML
)

COLUMN_SIZE = 4


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


def make_html(file_name: str, data: Dict[str, Any]) -> str:

    # templateファイルを取得
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    template = env.get_template(file_name)

    # htmlをレンダリング
    return template.render(data)


def save_html(file_path: str, html:str) -> None:
    with open(file_path, mode="w", encoding="utf-8") as f:
        f.write(html)


def count_daily_access(access_logs: List[AccessLog]) -> Dict[str, int]:
    access_by_day = defaultdict(int)
    for access_log in access_logs:
        day = access_log.date_time.strftime(DATE_KEY_FMT)
        access_by_day[day] += 1
    return access_by_day


def analyse_default_route():
    print("Start analysing default route /")


def analyse_create_route():

    # アクセスログを取得
    access_logs = download_logs(AccessRoute.CREATE.log_path)

    # クエリごとにログを集計
    texts = set()
    sizes = defaultdict(int)
    horizontals = 0
    layouts = {
        "タテ": {
            "small": 0,
            "middle": 0,
            "large": 0
        },
        "ヨコ": {
            "small": 0,
            "middle": 0,
            "large": 0
        }
    }
    for log in access_logs:
        texts.add(log.queries.get("text", None))
        sizes[log.queries.get("font-size", None)] += 1
        horizontals += bool(log.queries.get("horizontal", None))

        # レイアウトを集計
        horizontal = "ヨコ" if log.queries.get("horizontal", None) else "タテ"
        size = log.queries.get("font-size", None)
        if size not in ("small", "middle", "large"):
            continue
        layouts[horizontal][size] += 1

    # 集計結果を出力
    # with open(ANALYSIS_TEXT, mode="a", encoding="utf-8") as wf:
    #     for text in texts:
    #         wf.write(str(text) + "\n")
    # for size, count in sizes.items():
    #     print(f"{size} = {count}")

    texts.remove("")

    # データを変換
    return {
        "texts": [[list(texts)[i + j * COLUMN_SIZE] for i in range(COLUMN_SIZE)]
                  for j in range(len(texts)//COLUMN_SIZE)],
        "layouts": layouts
    }


def analyse_download_route():

    # アクセスログを取得
    access_logs = download_logs(AccessRoute.DOWNLOAD.log_path)

    # ダウンロードファイルごとに数を集計
    files = defaultdict(int)
    for log in access_logs:
        files[log.queries.get("key")] += 1

    return {
        "file_count": {
            key.split("/")[-1]: value
            for key, value in files.items()
            if key
        }
    }


def analyse_all_route() -> Dict[str, Any]:

    # アクセスログを全て取得
    default_access_logs = download_logs(AccessRoute.DEFAULT.log_path)
    create_access_logs = download_logs(AccessRoute.CREATE.log_path)
    download_access_logs = download_logs(AccessRoute.DOWNLOAD.log_path)
    all_access_logs = []
    all_access_logs.extend(default_access_logs)
    all_access_logs.extend(create_access_logs)
    all_access_logs.extend(download_access_logs)

    # 日にちごとのアクセス数を計算
    daily_create_access = count_daily_access(create_access_logs)
    daily_download_access = count_daily_access(download_access_logs)
    daily_all_access = count_daily_access(all_access_logs)

    # データの作成
    return {
        "main_page": {
            "access_count": len(default_access_logs),
            "user_count": count_user(default_access_logs)
        },
        "create_page": {
            "access_count": len(create_access_logs),
            "user_count": count_user(create_access_logs)
        },
        "download_page": {
            "access_count": len(download_access_logs),
            "user_count": count_user(download_access_logs)
        },
        "all_page": {
            "access_count": len(all_access_logs),
            "user_count": count_user(all_access_logs)
        },
        "days": list(daily_all_access.keys()),
        "daily_all_access": list(daily_all_access.values()),
        "daily_create_access": list(daily_create_access.values()),
        "daily_download_access": list(daily_download_access.values())
    }


def output_html():
    print("Start making html file.")

    # データの作成
    data = {
        "all": analyse_all_route(),
        "create": analyse_create_route(),
        "download": analyse_download_route()
    }

    # HTMLの作成
    html = make_html(OUTPUT_HTML, data)

    # HTMLを保存
    save_html(RENDERED_HTML_PATH, html)


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
    OUTPUT = (
        "output",
        output_html
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
