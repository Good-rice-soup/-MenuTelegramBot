from dataclasses import dataclass
from typing import Any


# TODO проставить нормальные типы
@dataclass
class User:
    user_id: Any
    state: Any
    switch: Any
    yellow_list: Any
    green_list: Any
    stop_list: Any
    list_of_dishes: Any
    parameters: Any
    list_of_variants: Any
    list_of_outputs: Any
    iteration: Any
