# `cuda_redist_find_features`

> [!IMPORTANT]
> This file is automatically generated -- do not make edits to it. Instead, edit [README_template.md](./nix/packages/regen-readme/README_template.md) and run `nix run .#regen-readme > README.md` to regenerate this file.

## Roadmap

- \[ \] Improve dependency resolution by being less strict with versions.
- \[ \] Further documentation.
- \[ \] Test cases.

## Overview

This package provides a script which finds the "features" of the redistributable packages NVIDIA provides for CUDA. It does this by using `redistrib_*.json` manifests from <https://developer.download.nvidia.com/compute/cuda/redist/> (and similar) and doing the following for each package:

1. Use `nix store prefetch-file` to download a package archive to the Nix store.

   - The manifest provides SHA256 hashes for each package, so we can verify the download.
   - Additionally, providing the expected hash allows us to avoid re-downloading archives.

1. Use `nix flake prefetch` on the store path of the archive to unpack it.

   - Though an abuse of the command, it does effectively serve as a way to unpack archives into the nix store.
   - It also allows us to avoid unpacking archives multiple times by short-circuiting to the store path if it already exists.

1. Evaluate the contents of the unpacked archive to decide what "features" it provides.

   - Implemented with heuristics. For example, if a directory contains a `lib` directory with a `libfoo.a` file, we assume that the package should have an output named `static` containing all its static libraries.

1. Write a complementary JSON file containing the "features" each package should have next to the manifest passed as argument to the script.

### Implemented Feature Detectors

These live in [detectors](./cuda_redist_find_features/manifest/feature/detectors).

- `cuda_architectures.py`: Runs `cuobjdump` on the unpacked archive to find the CUDA architectures it supports.
- `dynamic_library.py`: Checks if the unpacked archive contains a `lib` directory with dynamic libraries.
- `executable.py`: Checks if the unpacked archive contains executables in `bin`.
- `header.py`: Checks if the unpacked archive contains a `include` directory with headers.
- `needed_libs.py`: Runs `patchelf --print-needed` on the unpacked archive to find the libraries it needs.
- `provided_libs.py`: Runs `patchelf --print-soname` on the unpacked archive to find the libraries it provides.
- `python_module.py`: Checks if the unpacked archive contains a `site-packages` directory with Python modules.
- `static_library.py`: Checks if the unpacked archive contains a `lib` directory with static libraries.

## Usage

The script is meant to be used as part of the process of updating the manifests or supported CUDA versions in Nixpkgs. It is not meant to be used directly by users.

There are two commands:

- `download-manifests`: Download manifests from NVIDIA's website.
- `process-manifests`: Process manifests and write JSON files containing "features" each package should have.
- `print-feature-schema`: Print the JSON schema a "feature" manifest will have.
- `print-manifest-schema`: Print the JSON schema used to parse NVIDIA manifests.

```regen-readme
nix run .# -- --help
```

### `download-manifests`

```regen-readme
nix run .# -- download-manifests --help
```

### `process-manifests`

```regen-readme
nix run .# -- process-manifests --help
```

### `print-feature-schema`

```regen-readme
nix run .# -- print-feature-schema
```

### `print-manifest-schema`

```regen-readme
nix run .# -- print-manifest-schema
```

## Examples

### cuTensor

<details><summary>download-manifests</summary>

```regen-readme
nix run .# -- download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --log-level INFO
```

</details>

<details><summary>download-manifests with --version</summary>

```regen-readme
nix run .# -- download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --log-level INFO --version 1.4.0
```

</details>

<details><summary>download-manifests with --min-version and --max-version</summary>

```regen-readme
nix run .# -- download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --log-level INFO --min-version 1.4.0 --max-version 1.6.2
```

</details>

<details><summary>process-manifests</summary>

Assuming

```console
nix run .# -- download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --log-level INFO --min-version 1.4.0 --max-version 1.6.2
```

was run previously,

```regen-readme
nix run .# -- process-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --log-level INFO
```

</details>