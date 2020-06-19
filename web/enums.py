from enum import Enum


class Env(Enum):
    LOCAL = "local"
    DEV  = "dev"
    PROD = "prod"

    @classmethod
    def value_of(cls, value):
        for e in cls:
            if e.value == value:
                return e
        raise ValueError(f"{value} is not env name.")
