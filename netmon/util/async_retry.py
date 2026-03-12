from collections.abc import Callable
import asyncio
from typing import TypeVar, Awaitable, Set, Optional, ParamSpec
import functools

T = TypeVar("T")
P = ParamSpec("P")

def async_retry(
    for_exceptions: Set[type[Exception]],
    backoff_seconds: Callable[[int], float] = lambda retries: retries ** 2.0,
    max_retries: Optional[int] = 4,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T]]]:
    """
    Асинхронный декоратор для повторного выполнения функции при исключениях.

    :param for_exceptions: Набор типов исключений, при которых делать ретрай.
    :param backoff_seconds: Функция вычисления задержки по номеру попытки.
    :param max_retries: Максимальное число повторов, None = бесконечно.
    """
    def wrapper(f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(f)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> T:
            retries = 0
            while True:
                try:
                    return await f(*args, **kwargs)
                except tuple(for_exceptions) as e:
                    retries += 1

                    if max_retries is not None and retries > max_retries:
                        raise e

                    delay = backoff_seconds(retries)

                    await asyncio.sleep(delay)
        return inner
    return wrapper
