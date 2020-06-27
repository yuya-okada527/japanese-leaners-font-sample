from enum import Enum


class Env(Enum):
    LOCAL = "local"
    DEV   = "dev"
    PROD  = "prod"

    @classmethod
    def name_of(cls, name):
        for e in cls:
            if e.value == name:
                return e
        raise ValueError(f"{name} is not env name.")


class FontSize(Enum):
    SMALL  = {"name": "small",  "pixel": 50, "practice_num": 4, "draw_on": (10, 20)}
    MIDDLE = {"name": "middle", "pixel": 60, "practice_num": 3, "draw_on": (10, 20)}
    LARGE  = {"name": "large",  "pixel": 80, "practice_num": 2, "draw_on": (7,  30)}

    @classmethod
    def name_of(cls, name):
        for e in cls:
            if e.value["name"] == name:
                return e
        raise ValueError(f"{name} is not font name.")

