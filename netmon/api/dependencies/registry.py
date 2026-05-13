from typing import Any


class DependenciesRegistry:
    def __init__(self) -> None:
        self.__dependencies: dict[str, Any] = {}

    def register(self, id: str, dependency: Any) -> None:
        self.__dependencies[id] = dependency

    def get[T: Any](self, id: str):
        """Generates fixed dependency function"""

        def fixed_dependency() -> T:
            dependency = self.__dependencies.get(id)

            if dependency is None:
                raise ValueError(f"can not find dependency with ID: {id}")

            return dependency

        return fixed_dependency


DI_REGISTRY = DependenciesRegistry()
