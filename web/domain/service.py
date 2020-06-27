from functools import lru_cache
from typing import List

from .models import WorkBook
from ..infra.s3 import S3Client
from ..config import settings
from ..enums import Env


WORKBOOK_PREFIX = "materials/workbooks"


@lru_cache
def get_workbooks() -> List[WorkBook]:
    if settings.env == Env.LOCAL:
        return [
            WorkBook(
                "materials/workbooks/新ひらがな練習ノート（五十音順）.pdf",
                "新ひらがな練習ノート（五十音順）.pdf"
            )
        ]
    workbook_objects = S3Client.list_objects(WORKBOOK_PREFIX)
    workbook_keys = [obj.key for obj in workbook_objects]
    return [WorkBook(key, key.split("/")[-1]) for key in workbook_keys if not key.endswith("/")]


@lru_cache
def get_workbook(key: str):
    workbook_object = S3Client.get_object(key)
    return workbook_object.get()["Body"].read()

