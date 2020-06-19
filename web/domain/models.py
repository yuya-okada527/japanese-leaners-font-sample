import dataclasses


@dataclasses.dataclass(frozen=True)
class WorkBook:
    key: str
    name: str
