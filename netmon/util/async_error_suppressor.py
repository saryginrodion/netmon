from collections.abc import Callable
from typing import TypeVar, Awaitable, ParamSpec
import functools

import structlog

T = TypeVar("T")
P = ParamSpec("P")


def async_suppress_exceptions(
    for_exceptions: set[type[Exception]],
    log: structlog.stdlib.BoundLogger | None = None,
    include_args: bool = True,
) -> Callable[[Callable[P, Awaitable[T]]], Callable[P, Awaitable[T | None]]]:
    """Асинхронный декоратор для логирования и игнорирования исключений.

    При проигнорированном эксепшене отдает None
    """

    def wrapper(f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T | None]]:
        @functools.wraps(f)
        async def inner(*args: P.args, **kwargs: P.kwargs) -> T | None:
            try:
                return await f(*args, **kwargs)
            except Exception as e:
                if log is not None:
                    log.warning(
                        "suppressed error",
                        error=str(e),
                        args=args if include_args else "not included",
                        kwargs=kwargs if include_args else "not included",
                    )

                if any([isinstance(e, exc_type) for exc_type in for_exceptions]):
                    return None

                raise e

        return inner

    return wrapper
