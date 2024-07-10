from pathlib import Path
import json

from cuda_redist_lib.index import mk_index

with open(
    Path("modules") / "data" / "indices" / "sha256-and-relative-path.json",
    "w",
    encoding="utf-8",
) as file:
    json.dump(
        mk_index().model_dump(
            by_alias=True,
            exclude_none=True,
            exclude_unset=True,
            mode="json",
        ),
        file,
        indent=2,
        sort_keys=True,
    )
    file.write("\n")
