from typing import Any


def chunked[T: Any](lst: list[T], size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]
