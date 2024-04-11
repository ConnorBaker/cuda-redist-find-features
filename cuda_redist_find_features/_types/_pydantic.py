from collections.abc import ItemsView, Iterator, KeysView, Mapping, Sequence, ValuesView
from functools import partial
from typing import Any, overload

from pydantic import BaseModel, ConfigDict, DirectoryPath, FilePath, HttpUrl, RootModel, TypeAdapter

# We can't use strict because some of our models have fields which are Pydantic Dataclasses, which don't support
# strict.
model_config = ConfigDict(
    populate_by_name=True,
    revalidate_instances="always",
    validate_assignment=True,
    validate_default=True,
)

# NOTE: pydantic.errors.PydanticUserError: Cannot use `config` when the type is a BaseModel, dataclass or TypedDict.
# These types can have their own config and setting the config via the `config` parameter to TypeAdapter will not
# override it, thus the `config` you passed to TypeAdapter becomes meaningless, which is probably not what you want.
PydanticTypeAdapter: partial[TypeAdapter[Any]] = partial(TypeAdapter, config=model_config)

FilePathTA: TypeAdapter[FilePath] = PydanticTypeAdapter(FilePath)
DirectoryPathTA: TypeAdapter[DirectoryPath] = PydanticTypeAdapter(DirectoryPath)
HttpUrlTA: TypeAdapter[HttpUrl] = PydanticTypeAdapter(HttpUrl)


class PydanticSequence[T](RootModel[Sequence[T]]):
    """
    Root model for a sequence.
    """

    model_config = model_config
    root: Sequence[T]

    def __len__(self) -> int:
        return self.root.__len__()

    def __getitem__(self, index: int) -> T:
        return self.root.__getitem__(index)

    def __iter__(self) -> Iterator[T]:  # pyright: ignore[reportIncompatibleMethodOverride]
        return self.root.__iter__()

    def __contains__(self, item: T) -> bool:
        return self.root.__contains__(item)


class PydanticMapping[K, V](RootModel[Mapping[K, V]]):
    """
    Root model for a mapping.
    """

    model_config = model_config
    root: Mapping[K, V]

    @overload
    def get(self, __key: K) -> V | None: ...

    @overload
    def get(self, __key: K, __default: V) -> V: ...

    @overload
    def get[T](self, __key: K, __default: T) -> V | T: ...

    def get[T](self, key: K, default: T = None) -> V | T:
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
