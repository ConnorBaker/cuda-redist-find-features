# `cuda_redist_find_features`

## Roadmap

- \[ \] Further documentation.
- \[ \] Support extracting information about supported capabilities from libraries.
  - This can be used to determine whether a library contains device code.
  - In particular, such information enables determining whether a `linux-sbsa` (Linux ARM server) package can be used as a fallback for `linux-aarch64` (NVIDIA Jetson device) in the case there is no `linux-aarch64` package available.
- \[ \] Test cases.

## Overview

This package provides a script which finds the outputs of the redistributable packages NVIDIA provides for CUDA. It does this by taking as input a file path to one of the `redistrib_*.json` manifests from <https://developer.download.nvidia.com/compute/cuda/redist/> and doing the following for each package:

1. Use `nix store prefetch-file` to download a package archive to the Nix store.

   - The manifest provides SHA256 hashes for each package, so we can verify the download.
   - Additionally, providing the expected hash allows us to avoid re-downloading archives.

1. Use `nix flake prefetch` on the store path of the archive to unpack it.

   - Though an abuse of the command, it does effectively serve as a way to unpack archives into the nix store.
   - It also allows us to avoid unpacking archives multiple times by short-circuiting to the store path if it already exists.

1. Evaluate the contents of the unpacked archive to decide what outputs it provides.

   - Implemented with heuristics. For example, if a directory contains a `lib` directory with a `libfoo.a` file, we assume that the package should have an output named `static` containing all its static libraries.

1. Write a complementary JSON file containing the outputs each package should have next to the manifest passed as argument to the script.

## Usage

The script is meant to be used as part of the process of updating the manifests or supported CUDA versions in Nixpkgs. It is not meant to be used directly by users.

When adding a new manifest, run the script with the path to the manifest as argument. For example:

```bash
python3 ./cuda_redist_find_features ../manifests/redistrib_12.2.0.json
```

Run with `--help` to see the available options.

### Nix

To use with Nix, simply use `nix run .# -- <args>`.
