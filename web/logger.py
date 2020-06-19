import logging

from .enums import Env
from .config import settings


def create_logger(file_name: str):
    # ロガーの作成
    log = logging.getLogger(file_name)

    # ログレベルの設定
    if settings.env == Env.PROD:
        # 本番環境はINFO
        log.setLevel(logging.INFO)
    else:
        # それ以外はDEBUG
        log.setLevel(logging.DEBUG)

    # 標準出力に出力する
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    return log

