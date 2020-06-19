import os
from pathlib import Path

from dotenv import load_dotenv

from .enums import Env


ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[1],
    ".env"
)


class __Settings:

    def __init__(self, path=ENV_FILE):
        # 指定パスに.envファイルが存在する場合読み込む
        if os.path.exists(path):
            load_dotenv(path, verbose=True)

        # 環境変数をセット
        self.env = Env.value_of(os.getenv("ENV", "local"))


settings = __Settings()
