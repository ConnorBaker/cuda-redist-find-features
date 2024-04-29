import json
import os

from cuda_redist_lib.index import mk_index

# Environment variable is provided by Nix via makeWrapper.
with open(os.environ["STAGE0_OUTPUT_PATH"], "w", encoding="utf-8") as file:
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
