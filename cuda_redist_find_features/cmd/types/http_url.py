import click
import pydantic


class HttpUrl(click.ParamType):
    name: str = "url"

    def convert(self, value: str, param: None | click.Parameter, ctx: None | click.Context) -> pydantic.HttpUrl:
        try:
            return pydantic.parse_obj_as(pydantic.HttpUrl, value)
        except ValueError as err:
            self.fail(f"{value} is not a valid URL: {err}", param, ctx)


HTTP_URL_PARAM_TYPE = HttpUrl()
