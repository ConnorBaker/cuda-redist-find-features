from collections.abc import ItemsView, KeysView, Mapping, ValuesView
from functools import partial
from typing import Any, Generic, TypeVar, overload

from pydantic import BaseModel, ConfigDict, DirectoryPath, Field, FilePath, HttpUrl, RootModel, TypeAdapter

# We can't use strict because some of our models have fields which are Pydantic Dataclasses, which don't support
# strict.
model_config = ConfigDict(
    frozen=True,
    populate_by_name=True,
    revalidate_instances="always",
    validate_assignment=True,
    validate_default=True,
)

# NOTE: pydantic.errors.PydanticUserError: Cannot use `config` when the type is a BaseModel, dataclass or TypedDict.
# These types can have their own config and setting the config via the `config` parameter to TypeAdapter will not
# override it, thus the `config` you passed to TypeAdapter becomes meaningless, which is probably not what you want.
PydanticTypeAdapter: partial[TypeAdapter[Any]] = partial(TypeAdapter, config=model_config)
PydanticFrozenField = partial(Field, frozen=True)

FilePathTA: TypeAdapter[FilePath] = PydanticTypeAdapter(FilePath)
DirectoryPathTA: TypeAdapter[DirectoryPath] = PydanticTypeAdapter(DirectoryPath)
HttpUrlTA: TypeAdapter[HttpUrl] = PydanticTypeAdapter(HttpUrl)


T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")


class PydanticMapping(RootModel[Mapping[K, V]], Generic[K, V]):
    """
    Root model for a mapping.
    """

    model_config = model_config
    root: Mapping[K, V]

    @overload
    def get(self, __key: K) -> V | None:
        ...

    @overload
    def get(self, __key: K, __default: V) -> V:
        ...

    @overload
    def get(self, __key: K, __default: T) -> V | T:
        ...

    def get(self, key: K, default: T = None) -> V | T:
        "D.get(k[,d]) -> D[k] if k in D, else d.  d defaults to None."
        return self.root.get(key, default)

    def keys(self):
        "D.keys() -> a set-like object providing a view on D's keys"
        return KeysView(self.root)

    def items(self):
        "D.items() -> a set-like object providing a view on D's items"
        return ItemsView(self.root)

    def values(self):
        "D.values() -> an object providing a view on D's values"
        return ValuesView(self.root)

    def __len__(self) -> int:
        return self.root.__len__()

    def __contains__(self, key: K) -> bool:
        return self.root.__contains__(key)

    def __getitem__(self, key: K) -> V:
        return self.root.__getitem__(key)


class PydanticObject(BaseModel):
    """
    Base model.
    """

    model_config = model_config
