from functools import lru_cache
from typing import List

from .models import WorkBook
from ..infra.s3 import S3Client
from ..config import settings
from ..enums import Env


WORKBOOK_PREFIX = "materials/workbooks"

WORKBOOK_ORDER = {
    ,
    "materials/workbooks/ひらがな練習ノート（五十音順）Normal版.pdf": 0,
    "materials/workbooks/ひらがな練習ノート（字形順）Normal版.pdf": 1,
    "materials/workbooks/カタカナ練習ノート（五十音順）Normal版.pdf": 2,
    "materials/workbooks/カタカナ練習ノート（字形順）Normal版.pdf": 3,
    "materials/workbooks/ひらがな練習ノート（五十音順）Light版.pdf": 4,
    "materials/workbooks/ひらがな練習ノート（字形順）Light版.pdf": 5,
    "materials/workbooks/カタカナ練習ノート（五十音順）Light版.pdf": 6,
    "materials/workbooks/カタカナ練習ノート（字形順）Light版.pdf": 7,
    "materials/workbooks/ひらがなカタカナの言葉.pdf": 8
}


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

    return sorted(
        [WorkBook(key, key.split("/")[-1]) for key in workbook_keys if not key.endswith("/")],
        key=lambda workbook: WORKBOOK_ORDER.get(workbook.key, 100)
    )


@lru_cache
def get_workbook(key: str):
    workbook_object = S3Client.get_object(key)
    return workbook_object.get()["Body"].read()

