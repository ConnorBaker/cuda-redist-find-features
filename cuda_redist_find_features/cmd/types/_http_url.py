import click
import pydantic

from cuda_redist_find_features.types import HttpUrlTA


class HttpUrl(click.ParamType):
    name: str = "url"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> pydantic.HttpUrl:
        try:
            return HttpUrlTA.validate_python(value)
        except pydantic.ValidationError as err:
            self.fail(f"{value} is not a valid URL: {err}", param, ctx)


HTTP_URL_PARAM_TYPE = HttpUrl()
