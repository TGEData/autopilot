import math
from enum import Enum
from django.db import connection, models

def parse_isnan(value):
    try:
        if math.isnan(value):
            value = None
    except TypeError:
        pass

    return value


class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((x.name, x.value) for x in cls)
