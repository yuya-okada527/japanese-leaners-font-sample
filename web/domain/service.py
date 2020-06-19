from typing import List

from .models import WorkBook


def get_workbooks() -> List[WorkBook]:
    workbooks = [
        WorkBook("name1", "#"),
        WorkBook("name2", "#")
    ]

    return workbooks
