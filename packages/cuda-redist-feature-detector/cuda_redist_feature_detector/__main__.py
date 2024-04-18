import json
from argparse import ArgumentParser, Namespace
from pathlib import Path

from cuda_redist_feature_detector.outputs import FeatureOutputs


def setup_argparse() -> ArgumentParser:
    parser: ArgumentParser = ArgumentParser()
    parser.add_argument("--store-path", type=Path, required=True, help="Store path to provide to the feature detector.")
    return parser


def main() -> None:
    args: Namespace = setup_argparse().parse_args()
    print(
        json.dumps(
            {"outputs": FeatureOutputs.of(args.store_path).model_dump(by_alias=True, mode="json")},
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
