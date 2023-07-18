import argparse
import json
import logging
from pathlib import Path

from cuda_redist_find_features import manifest, outputs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="[%(asctime)s][PID%(process)s][%(funcName)s][%(levelname)s] %(message)s",
        # Use ISO8601 format for the timestamp
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    manifest_path: Path = args.manifest

    manifest_redist: dict[str, manifest.Package] = manifest.parse_manifest(manifest_path)
    manifest_outputs: dict[str, outputs.Package] = outputs.process_manifest(manifest_redist)
    # Write to a JSON file in the same directory as manifest_path
    filename = manifest_path.name.replace("redistrib", "redistrib_outputs")

    # Print summary information
    logging.info(f"Processed {len(manifest_outputs)} packages.")
    for package_name, package in manifest_outputs.items():
        logging.info(f"Package: {package_name}")
        logging.info(f"Description: {package.name}")
        for arch, release_features in package.get_architectures().items():
            if release_features is None:
                continue

            nix_outputs = release_features.get_outputs()
            logging.info(f"{arch} outputs: {sorted(nix_outputs)}.")
            logging.info(f"{arch} roots: {sorted(release_features.root_dirs)}")

    with manifest_path.with_name(filename).open("w") as f:
        json.dump(
            {
                package_name: package.dict(
                    by_alias=True,
                    exclude_none=True,
                    exclude={"name", "version", "license"},
                )
                for package_name, package in manifest_outputs.items()
            },
            f,
            indent=2,
            sort_keys=True,
        )
