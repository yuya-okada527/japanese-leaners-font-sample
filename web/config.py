import os
from pathlib import Path

from dotenv import load_dotenv

from .enums import Env


ENV_FILE = os.path.join(
    Path(__file__).resolve().parents[1],
    ".env"
)

DEFAULT_FONT_PATH = os.path.join(
    Path(__file__).resolve().parents[2],
    "fonts",
    "ttf",
    "JapaneseLearners1.ttf"
)


class __Settings:

    def __init__(self, path=ENV_FILE):
        # 指定パスに.envファイルが存在する場合読み込む
        if os.path.exists(path):
            load_dotenv(path, verbose=True)

        # 環境変数をセット
        self.env = Env.value_of(os.getenv("ENV", "local"))
        self.s3_bucket_name = os.getenv("S3_BUCKET_NAME")
        self.s3_access_key = os.getenv("S3_USER_ACCESS_KEY")
        self.s3_secret_key = os.getenv("S3_USER_SECRET_KEY")
        self.fonts_path = os.getenv("FONTS_PATH", DEFAULT_FONT_PATH)


settings = __Settings()
