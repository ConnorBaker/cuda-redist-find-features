import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from cuda_redist_feature_detector.outputs import FeatureOutputs


def setup_argparse() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--store-path", type=Path, required=True, help="Store path to provide to the feature detector.")
    parser.add_argument("--output-path", type=Path, required=True, help="Path to write the output JSON.")
    return parser


def main() -> None:
    args: Namespace = setup_argparse().parse_args()
    with open(args.output_path, "w", encoding="utf-8") as file:
        json.dump(
            FeatureOutputs.of(args.store_path).model_dump(by_alias=True, mode="json"),
            file,
            indent=2,
            sort_keys=True,
        )
        file.write("\n")


if __name__ == "__main__":
    main()
