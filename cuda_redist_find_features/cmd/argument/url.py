import logging

import click
from pydantic import HttpUrl

from ..types import HTTP_URL_PARAM_TYPE


def _url_argument_callback(ctx: click.Context, param: click.Parameter, url: HttpUrl) -> HttpUrl:
    if url:
        logging.info(f"Using URL {url}.")
    return url


url_argument = click.argument(
    "url",
    type=HTTP_URL_PARAM_TYPE,
    callback=_url_argument_callback,
)
