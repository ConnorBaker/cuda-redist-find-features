import logging

import click
from pydantic import HttpUrl

from ..types import HTTP_URL_OPTION


def _url_callback(ctx: click.Context, param: click.Parameter, url: HttpUrl) -> HttpUrl:
    if url:
        logging.info(f"Using URL {url}.")
    return url


url = click.argument(
    "url",
    type=HTTP_URL_OPTION,
    callback=_url_callback,
)
