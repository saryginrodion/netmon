from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Entry[T]:
    ttl: timedelta | None
    created_at: datetime
    value: T

class InMemoryStorage[T]:
    """Key Value хранилище с поддержкой TTL"""

    def __init__(self) -> None:
        self._storage: dict[str, Entry[T]] = {}

    def add(self, key: str, value: T, ttl: timedelta | None = None) -> bool:
        """Добавить значение. Возвращает True, если значение было заменено."""
        is_exists = self.get(key) is not None
        self._storage[key] = Entry(ttl=ttl, created_at=datetime.now(), value=value)

        return is_exists

    def remove(self, key: str) -> bool:
        """Удалить значение. Возвращает True, если значение было."""
        if self.get(key) is not None:
            del self._storage[key]
            return True

        return False

    def get(self, key: str) -> T | None:
        val = self._storage.get(key)

        if val is None:
            return None

        if val.ttl is None:
            return val.value

        if (datetime.now() - val.created_at) > val.ttl:
            del self._storage[key]
            return None

        return val.value

    def clear_expired(self) -> None:
        """Удалить все записи, у которых вышло время жизни"""
        for key in list(self._storage.keys()):
            self.get(key)
