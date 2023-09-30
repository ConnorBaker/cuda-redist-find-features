from typing import TypeVar

import click

from cuda_redist_find_features import version

# Type variable to denote that the value is whatever it was when it was passed in.
# We shouldn't use (None | version.Version) -> (None | version.Version) because that would allow us to return a
# version.Version when we were passed None.
NoneOrVersion = TypeVar("NoneOrVersion", None, version.Version)


class Version(click.ParamType):
    name: str = "version"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> version.Version:
        try:
            return version.Version.model_validate_strings(value)
        except ValueError:
            self.fail(f"{value} is not a valid version string", param, ctx)


VERSION_PARAM_TYPE = Version()
