"""Very small subset of Pydantic v1 style API used in tests."""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional


class FieldInfo:
    def __init__(self, default: Any = ..., *, default_factory: Optional[Callable[[], Any]] = None, description: str | None = None) -> None:
        self.default = default
        self.default_factory = default_factory
        self.description = description


def Field(default: Any = ..., *, default_factory: Optional[Callable[[], Any]] = None, description: str | None = None) -> FieldInfo:
    return FieldInfo(default=default, default_factory=default_factory, description=description)


class ModelMeta(type):
    def __new__(cls, name: str, bases: tuple[type, ...], namespace: Dict[str, Any]) -> "ModelMeta":
        field_defaults: Dict[str, FieldInfo] = {}
        for key, value in list(namespace.items()):
            if isinstance(value, FieldInfo):
                field_defaults[key] = value
                namespace[key] = value.default if value.default is not ... else None
        namespace["__field_defaults__"] = field_defaults
        return super().__new__(cls, name, bases, namespace)


class BaseModel(metaclass=ModelMeta):
    __field_defaults__: Dict[str, FieldInfo]

    def __init__(self, **data: Any) -> None:
        annotations = getattr(self, "__annotations__", {})
        for name in annotations:
            if name in data:
                value = data[name]
            elif name in self.__field_defaults__:
                field = self.__field_defaults__[name]
                if field.default is not ...:
                    value = field.default
                elif field.default_factory is not None:
                    value = field.default_factory()
                else:
                    value = None
            elif hasattr(self.__class__, name):
                value = getattr(self.__class__, name)
            else:
                value = None
            setattr(self, name, value)
        for name, value in data.items():
            if name not in annotations:
                setattr(self, name, value)

    def model_dump(self) -> Dict[str, Any]:
        annotations = getattr(self, "__annotations__", {})
        return {name: getattr(self, name, None) for name in annotations}
