from typing import TypeVar

import click

from cuda_redist_find_features._types import Version as _Version
from cuda_redist_find_features._types import VersionTA

# Type variable to denote that the value is whatever it was when it was passed in.
# We shouldn't use (None | version.Version) -> (None | version.Version) because that would allow us to return a
# version.Version when we were passed None.
NoneOrVersion = TypeVar("NoneOrVersion", None, _Version)


class Version(click.ParamType):
    name: str = "version"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> _Version:
        try:
            return VersionTA.validate_strings(value)
        except ValueError:
            self.fail(f"{value} is not a valid version string", param, ctx)


VERSION_PARAM_TYPE = Version()
