import logging
import pathlib
from typing import Callable

import click


def _manifest_dir_argument_callback(
    ctx: click.Context, param: click.Parameter, manifest_dir: pathlib.Path
) -> pathlib.Path:
    if manifest_dir:
        logging.debug(f"Using dir {manifest_dir}.")
    return manifest_dir


def manifest_dir_argument(
    exists: bool = False,
    file_okay: bool = True,
    dir_okay: bool = True,
    writable: bool = False,
    readable: bool = True,
    resolve_path: bool = False,
    allow_dash: bool = False,
    executable: bool = False,
) -> Callable[[click.decorators.FC], click.decorators.FC]:
    return click.argument(
        "manifest_dir",
        type=click.Path(
            path_type=pathlib.Path,
            exists=exists,
            file_okay=file_okay,
            dir_okay=dir_okay,
            writable=writable,
            readable=readable,
            resolve_path=resolve_path,
            allow_dash=allow_dash,
            executable=executable,
        ),
        callback=_manifest_dir_argument_callback,
    )
