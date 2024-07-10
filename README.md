# `cuda_redist_find_features`

> [!Important]
>
> This repo is in a transitory stage. It should be moved to `nix-community` or in-tree in Nixpkgs.

> [!Note]
>
> The `tensorrt` directory contains hand-made manifests meant to mimic the structure of NVIDIA's manifests for their other redistributables. They add TensorRT to the generated index.

## Roadmap

- \[ \] Move to `nix-community` or in-tree in Nixpkgs.
- \[ \] Improve dependency resolution by being less strict with versions.
- \[ \] Further documentation.
- \[ \] Test cases.

## Overview

This flake provides several tools to help maintain the CUDA redistributable packages in Nixpkgs. It is meant to be used as part of the process of updating the manifests or supported CUDA versions in Nixpkgs. It is not meant to be used directly by users.

### `mk-index-of-sha256-and-relative-path`

Retrieves and processes the manifests from NVIDIA's website. The result is a deeply-nested JSON object where the keys are various fields, and the leaves of the tree are the SRI hashes of the tarballs and the relative path to the tarball, if we cannot reconstruct it from the context of the tree.

### `mk-index-of-package-info`

- Unpacks the tarballs and creates a mapping between tarball hash and the store path of the unpacked tarball.
- Creates a mapping between the unpacked tarball store path and a feature object, describing the functionality (and directory structure) of the redistributable. This information is used by Nixpkgs to determine which outputs to provide.
- Creates a mapping between the unpacked tarball store path and the recursive NAR hash of the unpacked tarball. This information is used by Nixpkgs to treat the redistributables as Fixed Output Derivations.
- Composes the results of the prior stages, creating a deeply-nested JSON object like `stage0`. Instead of the values being the SRI hashes of the tarballs, they are the NAR hashes of the unpacked tarballs, which map to the feature object for that redistributable.

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
>
> `mk-index-of-package-info` requires a large amount of free space in the Nix store, since it will download every tarball from every NVIDIA manifest and unpack it.

Make the indices with:

```bash
nix run --builders "" --offline --accept-flake-config -L .#mk-indices
```
