# `cuda_redist_find_features`

> [!Important]
> This repo is in a transitory stage. It should be moved to `nix-community` or in-tree in Nixpkgs.

## Roadmap

- \[ \] Move to `nix-community` or in-tree in Nixpkgs.
- \[ \] Improve dependency resolution by being less strict with versions.
- \[ \] Further documentation.
- \[ \] Test cases.

## Overview

This flake provides several tools to help maintain the CUDA redistributable packages in Nixpkgs. It is meant to be used as part of the process of updating the manifests or supported CUDA versions in Nixpkgs. It is not meant to be used directly by users.

### `stage0`

Retrieves and processes the manifests from NVIDIA's website. The result is a deeply-nested JSON object where the keys are various fields, and the leaves of the tree are the SRI hashes of the tarballs.

### `stage1`

Unpacks the tarballs and computes their recursive NAR hash, so we can package them as Fixed Output Derivations. The result is a deeply-nested JSON object, just as in `stage0`, but with the SRI hashes replaced by the NAR hashes.

### `stage2`

Computes the "features" of the packages. The result is a deeply-nested JSON object, just as in `stage1`, but the NAR hashes now map to a `feature` attribute set describing the features of the package.

#### Implemented Feature Detectors

These live in [detectors](./packages/cuda-redist-feature-detector/cuda_redist_feature_detector/detectors).

- `cuda_architectures.py`: Runs `cuobjdump` on the unpacked archive to find the CUDA architectures it supports.
- `cuda_versions_in_lib.py`: Checks for subdirectories in `lib` named after CUDA versions.
- `dynamic_library.py`: Checks if the unpacked archive contains a `lib` directory with dynamic libraries.
- `executable.py`: Checks if the unpacked archive contains executables in `bin`.
- `header.py`: Checks if the unpacked archive contains a `include` directory with headers.
- `needed_libs.py`: Runs `patchelf --print-needed` on the unpacked archive to find the libraries it needs.
- `provided_libs.py`: Runs `patchelf --print-soname` on the unpacked archive to find the libraries it provides.
- `python_module.py`: Checks if the unpacked archive contains a `site-packages` directory with Python modules.
- `static_library.py`: Checks if the unpacked archive contains a `lib` directory with static libraries.
- `stubs.py`: Checks if the unpacked archive contains a `stubs` or `lib/stubs` directory.

## Usage

> [!Important]
> Stage 1 requires a large amount of free space in the Nix store. Since Stage 1 will download every tarball from every NVIDIA manifest and unpack it, it will take a while.

Run all the stages with:

```bash
nix run --builders "" -L .#stages
```

The script also accepts arguments, which you can see with the `--help` flag:

```console
$ nix run --builders "" -L .#stages -- --help
Usage: stages [--start <start>] [--stop <stop>]
  --start: The stage to start at (default: 0)
  --stop: The stage to stop at (default: 4)
```

These arguments are helpful if you want to run only a subset of the stages. For example, you might run `stage0` separately to generate the first index, and then manually delete some items from it to avoid processing them. This is especially useful if there is a new redistributable manifest, but you'd like to avoid redownloading unrelated artifacts you don't have cached.