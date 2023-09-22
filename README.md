# `cuda_redist_find_features`

## Roadmap

- \[ \] Further documentation.
- \[ \] Support extracting information about supported capabilities from libraries.
  - This can be used to determine whether a library contains device code.
  - In particular, such information enables determining whether a `linux-sbsa` (Linux ARM server) package can be used as a fallback for `linux-aarch64` (NVIDIA Jetson device) in the case there is no `linux-aarch64` package available.
- \[ \] Test cases.

## Overview

This package provides a script which finds the outputs of the redistributable packages NVIDIA provides for CUDA. It does this by using `redistrib_*.json` manifests from <https://developer.download.nvidia.com/compute/cuda/redist/> (and similar) and doing the following for each package:

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

There are two main modes of operation:

- `download-manifests`: Download manifests from NVIDIA's website.
- `process-manifests`: Process manifests and write JSON files containing the outputs each package should have.

```console
$ nix run .# -- --help
Usage: cuda-redist-find-features [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --no-parallel / --parallel  Disable parallel processing.
  --version VERSION           Version to accept. If not specified, operates on
                              all versions. Exclusive with --min-version and
                              --max-version.
  --min-version VERSION       Minimum version to accept. Exclusive with
                              --version.
  --max-version VERSION       Maximum version to accept. Exclusive with
                              --version.
  --help                      Show this message and exit.

Commands:
  download-manifests  Downloads manifest files found at URL to MANIFEST_DIR.
  process-manifests   Retrieves all manifests matching `redistrib_*.json`...
```

### `download-manifests`

```console
$ nix run .# -- download-manifests --help
Usage: cuda-redist-find-features download-manifests [OPTIONS] URL MANIFEST_DIR

  Downloads manifest files found at URL to MANIFEST_DIR.

  URL should not include a trailing slash.

  Neither MANIFEST_DIR nor its parent directory need to exist.

  Example:     download_manifests
  https://developer.download.nvidia.com/compute/cutensor/redist
  /tmp/cutensor_manifests

Options:
  --help  Show this message and exit.
```

### `process-manifests`

```console
$ nix run .# -- process-manifests --help
Usage: cuda-redist-find-features process-manifests [OPTIONS] URL_PREFIX
                                                   MANIFEST_DIR

  Retrieves all manifests matching `redistrib_*.json` in MANIFEST_DIR and
  processes them, using URL_PREFIX as the base URL.

  Downloads all packages in the manifest, checks them to see what features
  they provide, and writes a new manifest with this information to
  MANIFEST_DIR.

  URL_PREFIX should not include a trailing slash.

  MANIFEST_DIR should be a directory containing JSON manifest(s).

Options:
  --cleanup / --no-cleanup  Delete downloaded files after processing.
  --help                    Show this message and exit.
```

## Examples

### cuTensor

<details><summary>download-manifests</summary>

```console
$ nix run .# -- --debug download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
[2023-09-21T19:19:45+0000][PID139401][get_manifest_refs][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-21T19:19:45+0000][PID139401][get_manifest_refs_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-21T19:19:45+0000][PID139401][get_manifest_refs_from_url][DEBUG] Searching with regex href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]...
[2023-09-21T19:19:45+0000][PID139401][get_manifest_refs][DEBUG] Found 8 manifests in 0.6284823417663574 seconds.
[2023-09-21T19:19:45+0000][PID141014][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.2.json...
[2023-09-21T19:19:45+0000][PID141015][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.3.json...
[2023-09-21T19:19:45+0000][PID141016][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-21T19:19:45+0000][PID141017][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json...
[2023-09-21T19:19:45+0000][PID141018][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json...
[2023-09-21T19:19:45+0000][PID141019][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json...
[2023-09-21T19:19:45+0000][PID141020][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json...
[2023-09-21T19:19:45+0000][PID141021][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.7.0.json...
[2023-09-21T19:19:45+0000][PID141017][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json in 0.05662822723388672 seconds.
[2023-09-21T19:19:45+0000][PID141020][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json in 0.056535959243774414 seconds.
[2023-09-21T19:19:45+0000][PID141019][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json in 0.05667614936828613 seconds.
[2023-09-21T19:19:45+0000][PID141016][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.058361053466796875 seconds.
[2023-09-21T19:19:45+0000][PID141014][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.2.json in 0.06099700927734375 seconds.
[2023-09-21T19:19:45+0000][PID141021][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.7.0.json in 0.06390595436096191 seconds.
[2023-09-21T19:19:45+0000][PID141018][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json in 0.06416010856628418 seconds.
[2023-09-21T19:19:45+0000][PID141015][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.3.json in 0.06646132469177246 seconds.
```

</details>

<details><summary>download-manifests with --version</summary>

```console
$ nix run .# -- --debug --version 1.4.0 download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
[2023-09-21T19:21:54+0000][PID146003][get_manifest_refs][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-21T19:21:55+0000][PID146003][get_manifest_refs_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-21T19:21:55+0000][PID146003][get_manifest_refs_from_url][DEBUG] Searching with regex href=['"]redistrib_(1\.4\.0)\.json['"]...
[2023-09-21T19:21:55+0000][PID146003][get_manifest_refs][DEBUG] Found 1 manifests in 0.22959542274475098 seconds.
[2023-09-21T19:21:55+0000][PID147649][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-21T19:21:55+0000][PID147649][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.06266927719116211 seconds.
```

</details>

<details><summary>download-manifests with --min-version and --max-version</summary>

```console
$ nix run .# -- --debug --min-version 1.4.0 --max-version 1.6.2 download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
warning: Git tree '/home/connorbaker/cuda-redist-find-features' is dirty
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs_from_url][DEBUG] Searching with regex href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]...
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs_from_url][DEBUG] Skipping href='redistrib_1.3.2.json' because its version 1.3.2 is older than the minimum version 1.4.0
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs_from_url][DEBUG] Skipping href='redistrib_1.3.3.json' because its version 1.3.3 is older than the minimum version 1.4.0
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs_from_url][DEBUG] Skipping href='redistrib_1.7.0.json' because its version 1.7.0 is newer than the maximum version 1.6.2
[2023-09-21T19:23:32+0000][PID149352][get_manifest_refs][DEBUG] Found 5 manifests in 0.2544560432434082 seconds.
[2023-09-21T19:23:32+0000][PID150965][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-21T19:23:32+0000][PID150966][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json...
[2023-09-21T19:23:32+0000][PID150967][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json...
[2023-09-21T19:23:32+0000][PID150968][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json...
[2023-09-21T19:23:32+0000][PID150969][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json...
[2023-09-21T19:23:32+0000][PID150965][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.04576683044433594 seconds.
[2023-09-21T19:23:32+0000][PID150967][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json in 0.0460362434387207 seconds.
[2023-09-21T19:23:32+0000][PID150969][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json in 0.051846981048583984 seconds.
[2023-09-21T19:23:32+0000][PID150968][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json in 0.05428171157836914 seconds.
[2023-09-21T19:23:32+0000][PID150966][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json in 0.05498957633972168 seconds.
```

</details>

<details><summary>process-manifests</summary>

```console
$ nix run .# -- --debug process-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
[2023-09-22T02:52:18+0000][PID241070][from_ref][DEBUG] Fetching manifests from cutensor_manifests...
[2023-09-22T02:52:18+0000][PID241070][_from_dir][DEBUG] Globbing for redistrib_[0123456789]*.json...
[2023-09-22T02:52:18+0000][PID241070][from_ref][DEBUG] Found 8 manifests in 0.00033926963806152344 seconds.
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.3.2.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.3.2.json in 1.8835067749023438e-05 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.3.2.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.3.2
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2021-09-22
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.3.3.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.3.3.json in 2.3126602172851562e-05 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.3.3.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.3.3
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2021-09-22
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.2.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.2.json in 1.4543533325195312e-05 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.2.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.6.2
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2022-12-12
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.4.0.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.4.0.json in 1.239776611328125e-05 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.4.0.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.4.0
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2021-11-19
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.0.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.0.json in 8.821487426757812e-06 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.0.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.6.0
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2022-06-24
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.5.0.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.5.0.json in 9.775161743164062e-06 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.5.0.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.5.0
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2022-03-08
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.1.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.1.json in 8.58306884765625e-06 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.1.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.6.1
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2022-10-05
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.7.0.json...
[2023-09-22T02:52:18+0000][PID241070][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.7.0.json in 8.58306884765625e-06 seconds.
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.7.0.json
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Version: 1.7.0
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][INFO] Release date: 2023-03-16
[2023-09-22T02:52:18+0000][PID241070][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-22T02:52:18+0000][PID242720][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242720][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242720][process_package][INFO] Version: 1.3.2.3
[2023-09-22T02:52:18+0000][PID242720][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242720][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.3.2.3-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242720][process_package][DEBUG] SHA256: 8a219f0bbbebabc9ad3ea70a77a84012fb4e3bc9da2808b1eca82b02e01d5113
[2023-09-22T02:52:18+0000][PID242720][process_package][DEBUG] MD5: 9a70cf2abd0ba85ea4b5ec9da619900f
[2023-09-22T02:52:18+0000][PID242721][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242720][process_package][DEBUG] Size: 202534904
[2023-09-22T02:52:18+0000][PID242720][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.3.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242721][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242722][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242721][process_package][INFO] Version: 1.3.3.2
[2023-09-22T02:52:18+0000][PID242722][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242723][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242722][process_package][INFO] Version: 1.6.2.3
[2023-09-22T02:52:18+0000][PID242721][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242721][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.3.3.2-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242723][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242721][process_package][DEBUG] SHA256: 79f294c4a7933e5acee5f150145c526d6cd4df16eefb63f2d65df1dbc683cd68
[2023-09-22T02:52:18+0000][PID242723][process_package][INFO] Version: 1.4.0.6
[2023-09-22T02:52:18+0000][PID242721][process_package][DEBUG] MD5: 1f632c9d33ffef9c819e10c95d69a134
[2023-09-22T02:52:18+0000][PID242722][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242721][process_package][DEBUG] Size: 202541908
[2023-09-22T02:52:18+0000][PID242722][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242722][process_package][DEBUG] SHA256: 558329fa05409f914ebbe218a1cf7c9ccffdb7aa2642b96db85fd78b5ad534d1
[2023-09-22T02:52:18+0000][PID242721][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.3.3.2-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242722][process_package][DEBUG] MD5: 8d5d129aa7863312a95084ab5a27b7e7
[2023-09-22T02:52:18+0000][PID242723][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242722][process_package][DEBUG] Size: 535585612
[2023-09-22T02:52:18+0000][PID242723][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242723][process_package][DEBUG] SHA256: 5da44ff2562ab7b9286122653e54f28d2222c8aab4bb02e9bdd4cf7e4b7809be
[2023-09-22T02:52:18+0000][PID242722][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242723][process_package][DEBUG] MD5: 6058c728485072c980f652c2de38b016
[2023-09-22T02:52:18+0000][PID242725][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242723][process_package][DEBUG] Size: 218951992
[2023-09-22T02:52:18+0000][PID242723][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242726][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242725][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242725][process_package][INFO] Version: 1.5.0.3
[2023-09-22T02:52:18+0000][PID242726][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242724][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242726][process_package][INFO] Version: 1.6.1.5
[2023-09-22T02:52:18+0000][PID242727][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-22T02:52:18+0000][PID242725][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242727][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242725][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] License: cuTensor
[2023-09-22T02:52:18+0000][PID242726][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242727][process_package][INFO] Version: 1.7.0.1
[2023-09-22T02:52:18+0000][PID242725][process_package][DEBUG] SHA256: ad736acc94e88673b04a3156d7d3a408937cac32d083acdfbd8435582cbe15db
[2023-09-22T02:52:18+0000][PID242726][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242725][process_package][DEBUG] MD5: bcdafb6d493aceebfb9a420880f1486c
[2023-09-22T02:52:18+0000][PID242726][process_package][DEBUG] SHA256: e895476ab13c4a28bdf018f23299746968564024783c066a2602bc0f09b86e47
[2023-09-22T02:52:18+0000][PID242725][process_package][DEBUG] Size: 208384668
[2023-09-22T02:52:18+0000][PID242726][process_package][DEBUG] MD5: c44194d2067ce296f9a2c51ddbd6eb7b
[2023-09-22T02:52:18+0000][PID242724][process_package][INFO] Version: 1.6.0.3
[2023-09-22T02:52:18+0000][PID242727][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242726][process_package][DEBUG] Size: 365411216
[2023-09-22T02:52:18+0000][PID242725][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242727][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.7.0.1-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242726][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242727][process_package][DEBUG] SHA256: af4ad5e29dcb636f1bf941ed1fd7fc8053eeec4813fbc0b41581e114438e84c8
[2023-09-22T02:52:18+0000][PID242727][process_package][DEBUG] MD5: 30739decf9f5267f2a5f28c7c1a1dc3d
[2023-09-22T02:52:18+0000][PID242727][process_package][DEBUG] Size: 538487672
[2023-09-22T02:52:18+0000][PID242727][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.7.0.1-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242724][process_package][INFO] Architecture: linux-ppc64le
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] SHA256: 6af9563a3581e1879dd17e9bae79ceae1b4084f45e735780125aab86056646eb
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] MD5: 38e3cd74fb7c0fa9c0836a9d172b9737
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] Size: 332890432
[2023-09-22T02:52:18+0000][PID242724][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242722][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz to the Nix store in 0.01264810562133789 seconds.
[2023-09-22T02:52:18+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/8gvv8lyz2qcjasxvxbq6mi3na8j4ncf1-libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242721][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.3.3.2-archive.tar.xz to the Nix store in 0.013230562210083008 seconds.
[2023-09-22T02:52:18+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/rr9mzpij9lb6ayzni2haf0vakl8jvgdf-libcutensor-linux-ppc64le-1.3.3.2-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242727][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.7.0.1-archive.tar.xz to the Nix store in 0.01374197006225586 seconds.
[2023-09-22T02:52:18+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/7la6i8zid632wsmimn2n0bya7kz0j5hm-libcutensor-linux-ppc64le-1.7.0.1-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242720][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.3.2.3-archive.tar.xz to the Nix store in 0.014499902725219727 seconds.
[2023-09-22T02:52:18+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/1x3z7yz7w8i30i6y6ijbn2klyzw1aij0-libcutensor-linux-ppc64le-1.3.2.3-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242723][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz to the Nix store in 0.015374898910522461 seconds.
[2023-09-22T02:52:18+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/5b7bmhi1l35i6kqx6rwxq2hxiicshkh4-libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242726][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz to the Nix store in 0.015949010848999023 seconds.
[2023-09-22T02:52:18+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/mcdm0ifn6lwnbrqskki5jnvrzs07vkpb-libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242724][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz to the Nix store in 0.016811370849609375 seconds.
[2023-09-22T02:52:18+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/897fvwmby7nc9ii3adshfn7f2f671bbs-libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242725][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz to the Nix store in 0.017687559127807617 seconds.
[2023-09-22T02:52:18+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/9fy3afhldjlgigyc09348nc50ccr7kq1-libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz...
[2023-09-22T02:52:18+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/897fvwmby7nc9ii3adshfn7f2f671bbs-libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz in 0.014842748641967773 seconds.
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:18+0000][PID242724][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:18+0000][PID242724][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] SHA256: 802f030de069e7eeec2e72f151471fc9776f0272a81804690c749373505dcb70
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] MD5: 38436011c8375ba78e2cd8c47182c6de
[2023-09-22T02:52:18+0000][PID242724][process_package][DEBUG] Size: 253328216
[2023-09-22T02:52:18+0000][PID242724][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:18+0000][PID242724][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz to the Nix store in 0.01350259780883789 seconds.
[2023-09-22T02:52:18+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/0fldgjlk64r6yfs383ra9kmqqhydjyxx-libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz...
[2023-09-22T02:52:27+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/rr9mzpij9lb6ayzni2haf0vakl8jvgdf-libcutensor-linux-ppc64le-1.3.3.2-archive.tar.xz in 8.88966965675354 seconds.
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 9 shared libraries.
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 3 static libraries.
[2023-09-22T02:52:27+0000][PID242721][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242721][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:27+0000][PID242721][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.3.3.2-archive.tar.xz
[2023-09-22T02:52:27+0000][PID242721][process_package][DEBUG] SHA256: 0b62d5305abfdfca4776290f16a1796c78c1fa83b203680c012f37d44706fcdb
[2023-09-22T02:52:27+0000][PID242721][process_package][DEBUG] MD5: e476675490aff0b154f2f38063f0c10b
[2023-09-22T02:52:27+0000][PID242721][process_package][DEBUG] Size: 149059520
[2023-09-22T02:52:27+0000][PID242721][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.3.3.2-archive.tar.xz to the Nix store...
[2023-09-22T02:52:27+0000][PID242721][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.3.3.2-archive.tar.xz to the Nix store in 0.013720989227294922 seconds.
[2023-09-22T02:52:27+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/syxzdnwk6bik6kc2p559lga3wbs9wr0n-libcutensor-linux-sbsa-1.3.3.2-archive.tar.xz...
[2023-09-22T02:52:27+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/9fy3afhldjlgigyc09348nc50ccr7kq1-libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz in 8.936951398849487 seconds.
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:27+0000][PID242725][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242725][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:27+0000][PID242725][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz
[2023-09-22T02:52:27+0000][PID242725][process_package][DEBUG] SHA256: 5b9ac479b1dadaf40464ff3076e45f2ec92581c07df1258a155b5bcd142f6090
[2023-09-22T02:52:27+0000][PID242725][process_package][DEBUG] MD5: 62149d726480d12c9a953d27edc208dc
[2023-09-22T02:52:27+0000][PID242725][process_package][DEBUG] Size: 156512748
[2023-09-22T02:52:27+0000][PID242725][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:27+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/1x3z7yz7w8i30i6y6ijbn2klyzw1aij0-libcutensor-linux-ppc64le-1.3.2.3-archive.tar.xz in 8.954383373260498 seconds.
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:27+0000][PID242725][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz to the Nix store in 0.013093233108520508 seconds.
[2023-09-22T02:52:27+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/5vb91ij9n4rbc0zj6118flzbx1dp3n8j-libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz...
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 9 shared libraries.
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 3 static libraries.
[2023-09-22T02:52:27+0000][PID242720][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242720][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:27+0000][PID242720][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.3.2.3-archive.tar.xz
[2023-09-22T02:52:27+0000][PID242720][process_package][DEBUG] SHA256: 6e92fee6a192f9fc19876df99544893f7b4cfb8b5ff1ce6d172474c6e13154ea
[2023-09-22T02:52:27+0000][PID242720][process_package][DEBUG] MD5: 2fa78066ec2d5a734e4fb2732b87756e
[2023-09-22T02:52:27+0000][PID242720][process_package][DEBUG] Size: 149057692
[2023-09-22T02:52:27+0000][PID242720][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.3.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:27+0000][PID242720][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.3.2.3-archive.tar.xz to the Nix store in 0.013858795166015625 seconds.
[2023-09-22T02:52:27+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/vbq8b32vzarri6x3scvp9prgff7szspx-libcutensor-linux-sbsa-1.3.2.3-archive.tar.xz...
[2023-09-22T02:52:27+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/5b7bmhi1l35i6kqx6rwxq2hxiicshkh4-libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz in 9.235002040863037 seconds.
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:27+0000][PID242723][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:27+0000][PID242723][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:27+0000][PID242723][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz
[2023-09-22T02:52:27+0000][PID242723][process_package][DEBUG] SHA256: 6b06d63a5bc49c1660be8c307795f8a901c93dcde7b064455a6c81333c7327f4
[2023-09-22T02:52:27+0000][PID242723][process_package][DEBUG] MD5: a6f3fd515c052df43fbee9508ea87e1e
[2023-09-22T02:52:27+0000][PID242723][process_package][DEBUG] Size: 163596044
[2023-09-22T02:52:27+0000][PID242723][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-22T02:52:28+0000][PID242723][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz to the Nix store in 0.013502359390258789 seconds.
[2023-09-22T02:52:28+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/jkzvn343kkanvldzp0apz0570zi766xg-libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz...
[2023-09-22T02:52:28+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/0fldgjlk64r6yfs383ra9kmqqhydjyxx-libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz in 9.813265085220337 seconds.
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-22T02:52:28+0000][PID242724][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:28+0000][PID242724][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:28+0000][PID242724][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz
[2023-09-22T02:52:28+0000][PID242724][process_package][DEBUG] SHA256: b07e32a37eee1df7d9330e6d7faf9baf7fffd58007e2544164ea30aec49a5281
[2023-09-22T02:52:28+0000][PID242724][process_package][DEBUG] MD5: 80ffc765748952385d3dbbaef262d72e
[2023-09-22T02:52:28+0000][PID242724][process_package][DEBUG] Size: 333834656
[2023-09-22T02:52:28+0000][PID242724][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:28+0000][PID242724][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz to the Nix store in 0.01306295394897461 seconds.
[2023-09-22T02:52:28+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/gyzp5pspbipp9nmn0sqdl05b01br1rl2-libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz...
[2023-09-22T02:52:38+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/vbq8b32vzarri6x3scvp9prgff7szspx-libcutensor-linux-sbsa-1.3.2.3-archive.tar.xz in 10.340870380401611 seconds.
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 2 static libraries.
[2023-09-22T02:52:38+0000][PID242720][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242720][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:38+0000][PID242720][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.3.2.3-archive.tar.xz
[2023-09-22T02:52:38+0000][PID242720][process_package][DEBUG] SHA256: cf2b8f1f220cdc90aaec577bde144509f805739e00a857ef161f6a5e8b769697
[2023-09-22T02:52:38+0000][PID242720][process_package][DEBUG] MD5: 0c73c3918dd893a8bdfec48de9e5c312
[2023-09-22T02:52:38+0000][PID242720][process_package][DEBUG] Size: 201844004
[2023-09-22T02:52:38+0000][PID242720][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.3.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:38+0000][PID242720][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.3.2.3-archive.tar.xz to the Nix store in 0.012814044952392578 seconds.
[2023-09-22T02:52:38+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/0ss5gzdi3g7bmha52pqla9l29i2gmv2x-libcutensor-linux-x86_64-1.3.2.3-archive.tar.xz...
[2023-09-22T02:52:38+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/syxzdnwk6bik6kc2p559lga3wbs9wr0n-libcutensor-linux-sbsa-1.3.3.2-archive.tar.xz in 10.712314128875732 seconds.
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 2 static libraries.
[2023-09-22T02:52:38+0000][PID242721][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242721][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:38+0000][PID242721][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz
[2023-09-22T02:52:38+0000][PID242721][process_package][DEBUG] SHA256: 2e9517f31305872a7e496b6aa8ea329acda6b947b0c1eb1250790eaa2d4e2ecc
[2023-09-22T02:52:38+0000][PID242721][process_package][DEBUG] MD5: 977699555cfcc8d2ffeff018a0f975b0
[2023-09-22T02:52:38+0000][PID242721][process_package][DEBUG] Size: 201849628
[2023-09-22T02:52:38+0000][PID242721][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz to the Nix store...
[2023-09-22T02:52:38+0000][PID242721][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz to the Nix store in 0.012905359268188477 seconds.
[2023-09-22T02:52:38+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/hqihs0z31dmd76ld4j7rlw3d77wmyd9m-libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz...
[2023-09-22T02:52:38+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/jkzvn343kkanvldzp0apz0570zi766xg-libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz in 10.772931098937988 seconds.
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-22T02:52:38+0000][PID242723][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:38+0000][PID242723][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:38+0000][PID242723][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz
[2023-09-22T02:52:38+0000][PID242723][process_package][DEBUG] SHA256: 467ba189195fcc4b868334fc16a0ae1e51574139605975cc8004cedebf595964
[2023-09-22T02:52:38+0000][PID242723][process_package][DEBUG] MD5: 5d4009390be0226fc3ee75d225053123
[2023-09-22T02:52:38+0000][PID242723][process_package][DEBUG] Size: 218277136
[2023-09-22T02:52:38+0000][PID242723][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-22T02:52:38+0000][PID242723][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz to the Nix store in 0.013013362884521484 seconds.
[2023-09-22T02:52:38+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/q7jcksly352yawl1l7yzzf7l376ziwa3-libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz...
[2023-09-22T02:52:39+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/mcdm0ifn6lwnbrqskki5jnvrzs07vkpb-libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz in 20.33694362640381 seconds.
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:39+0000][PID242726][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:39+0000][PID242726][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:39+0000][PID242726][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz
[2023-09-22T02:52:39+0000][PID242726][process_package][DEBUG] SHA256: f0644bbdca81b890056a7b92714e787333b06a4bd384e4dfbdc3938fbd132e65
[2023-09-22T02:52:39+0000][PID242726][process_package][DEBUG] MD5: a1c841dd532e7aef6963452439042f09
[2023-09-22T02:52:39+0000][PID242726][process_package][DEBUG] Size: 288691268
[2023-09-22T02:52:39+0000][PID242726][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-22T02:52:39+0000][PID242726][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz to the Nix store in 0.013107061386108398 seconds.
[2023-09-22T02:52:39+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/qz1hpcq6nxv0z0n0p1rjdg2ag2kyi7g1-libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz...
[2023-09-22T02:52:39+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/5vb91ij9n4rbc0zj6118flzbx1dp3n8j-libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz in 11.41628360748291 seconds.
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-22T02:52:39+0000][PID242725][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:39+0000][PID242725][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:39+0000][PID242725][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz
[2023-09-22T02:52:39+0000][PID242725][process_package][DEBUG] SHA256: 4fdebe94f0ba3933a422cff3dd05a0ef7a18552ca274dd12564056993f55471d
[2023-09-22T02:52:39+0000][PID242725][process_package][DEBUG] MD5: 7e1b1a613b819d6cf6ee7fbc70f16105
[2023-09-22T02:52:39+0000][PID242725][process_package][DEBUG] Size: 208925360
[2023-09-22T02:52:39+0000][PID242725][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:39+0000][PID242725][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz to the Nix store in 0.012919187545776367 seconds.
[2023-09-22T02:52:39+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/k5xq37i1j3w710ppy8v0qqg91pkdxflc-libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz...
[2023-09-22T02:52:50+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/8gvv8lyz2qcjasxvxbq6mi3na8j4ncf1-libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz in 31.717438220977783 seconds.
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-22T02:52:50+0000][PID242722][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:52:50+0000][PID242722][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:50+0000][PID242722][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz
[2023-09-22T02:52:50+0000][PID242722][process_package][DEBUG] SHA256: 7d4d9088c892bb692ffd70750b49625d1ccbb85390f6eb7c70d6cf582df6d935
[2023-09-22T02:52:50+0000][PID242722][process_package][DEBUG] MD5: f6e0cce3a3b38ced736e55a19da587a3
[2023-09-22T02:52:50+0000][PID242722][process_package][DEBUG] Size: 450705724
[2023-09-22T02:52:50+0000][PID242722][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:52:50+0000][PID242722][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz to the Nix store in 0.012977838516235352 seconds.
[2023-09-22T02:52:50+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/gj9hgzj57jvnbh9h2rvqd957366d00k8-libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz...
[2023-09-22T02:52:52+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/gyzp5pspbipp9nmn0sqdl05b01br1rl2-libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz in 24.151889324188232 seconds.
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:52+0000][PID242724][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:52+0000][PID242724][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:52:52+0000][PID242724][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.0.3-archive.zip
[2023-09-22T02:52:52+0000][PID242724][process_package][DEBUG] SHA256: e8875e43d8c4169dc65095cb81c5d1e4120f664b4e2288658d73a4a2c2558f3c
[2023-09-22T02:52:52+0000][PID242724][process_package][DEBUG] MD5: 4c76fb8d24296d644033bc992e4159e4
[2023-09-22T02:52:52+0000][PID242724][process_package][DEBUG] Size: 624418613
[2023-09-22T02:52:52+0000][PID242724][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.0.3-archive.zip to the Nix store...
[2023-09-22T02:52:52+0000][PID242724][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.0.3-archive.zip to the Nix store in 0.013149261474609375 seconds.
[2023-09-22T02:52:52+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/ccl9i73nxn1vp47wq8a5mpnp68khdz2z-libcutensor-windows-x86_64-1.6.0.3-archive.zip...
[2023-09-22T02:52:53+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/7la6i8zid632wsmimn2n0bya7kz0j5hm-libcutensor-linux-ppc64le-1.7.0.1-archive.tar.xz in 34.559409379959106 seconds.
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-22T02:52:53+0000][PID242727][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242727][process_package][INFO] Architecture: linux-sbsa
[2023-09-22T02:52:53+0000][PID242727][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.7.0.1-archive.tar.xz
[2023-09-22T02:52:53+0000][PID242727][process_package][DEBUG] SHA256: c31f8e4386539434a5d1643ebfed74572011783b4e21b62be52003e3a9de3720
[2023-09-22T02:52:53+0000][PID242727][process_package][DEBUG] MD5: 3185c17e8f32c9c54f591006b917365e
[2023-09-22T02:52:53+0000][PID242727][process_package][DEBUG] Size: 454324456
[2023-09-22T02:52:53+0000][PID242727][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.7.0.1-archive.tar.xz to the Nix store...
[2023-09-22T02:52:53+0000][PID242727][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.7.0.1-archive.tar.xz to the Nix store in 0.013684511184692383 seconds.
[2023-09-22T02:52:53+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/spqx52qx2g7g7gr805870j9csvg6f3h0-libcutensor-linux-sbsa-1.7.0.1-archive.tar.xz...
[2023-09-22T02:52:53+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/0ss5gzdi3g7bmha52pqla9l29i2gmv2x-libcutensor-linux-x86_64-1.3.2.3-archive.tar.xz in 15.39250373840332 seconds.
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 9 shared libraries.
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 3 static libraries.
[2023-09-22T02:52:53+0000][PID242720][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242720][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:52:53+0000][PID242720][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.3.2.3-archive.zip
[2023-09-22T02:52:53+0000][PID242720][process_package][DEBUG] SHA256: 7c7880de9c15db1d45cc24ce5758fcf9d1cd596139cfb57c97c2f764d86794b7
[2023-09-22T02:52:53+0000][PID242720][process_package][DEBUG] MD5: b1a15df717b9aee125583150dda30150
[2023-09-22T02:52:53+0000][PID242720][process_package][DEBUG] Size: 374934832
[2023-09-22T02:52:53+0000][PID242720][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.3.2.3-archive.zip to the Nix store...
[2023-09-22T02:52:53+0000][PID242720][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.3.2.3-archive.zip to the Nix store in 0.014507532119750977 seconds.
[2023-09-22T02:52:53+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/1n8xrchy7im8v746vqjjj4s6jqhciv8g-libcutensor-windows-x86_64-1.3.2.3-archive.zip...
[2023-09-22T02:52:53+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/hqihs0z31dmd76ld4j7rlw3d77wmyd9m-libcutensor-linux-x86_64-1.3.3.2-archive.tar.xz in 15.137640953063965 seconds.
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 9 shared libraries.
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 3 static libraries.
[2023-09-22T02:52:53+0000][PID242721][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242721][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:52:53+0000][PID242721][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.3.3.2-archive.zip
[2023-09-22T02:52:53+0000][PID242721][process_package][DEBUG] SHA256: 3abeacbe7085af7026ca1399a77c681c219c10a1448a062964e97aaac2b05851
[2023-09-22T02:52:53+0000][PID242721][process_package][DEBUG] MD5: fe75f031c53260c00ad5f7c5d69d31e5
[2023-09-22T02:52:53+0000][PID242721][process_package][DEBUG] Size: 374926147
[2023-09-22T02:52:53+0000][PID242721][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.3.3.2-archive.zip to the Nix store...
[2023-09-22T02:52:53+0000][PID242721][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.3.3.2-archive.zip to the Nix store in 0.013558387756347656 seconds.
[2023-09-22T02:52:53+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/jbs6pjc4z4mn5pa392s84dad5nskysh0-libcutensor-windows-x86_64-1.3.3.2-archive.zip...
[2023-09-22T02:52:53+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/k5xq37i1j3w710ppy8v0qqg91pkdxflc-libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz in 14.525056600570679 seconds.
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:53+0000][PID242725][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242725][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:52:53+0000][PID242725][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.5.0.3-archive.zip
[2023-09-22T02:52:53+0000][PID242725][process_package][DEBUG] SHA256: de76f7d92600dda87a14ac756e9d0b5733cbceb88bcd20b3935a82c99342e6cd
[2023-09-22T02:52:53+0000][PID242725][process_package][DEBUG] MD5: 66feef08de8c7fccf7269383e663fd06
[2023-09-22T02:52:53+0000][PID242725][process_package][DEBUG] Size: 421810766
[2023-09-22T02:52:53+0000][PID242725][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.5.0.3-archive.zip to the Nix store...
[2023-09-22T02:52:53+0000][PID242725][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.5.0.3-archive.zip to the Nix store in 0.013339757919311523 seconds.
[2023-09-22T02:52:53+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/66s6g8dx81akm36p1fh8vz4r3m2dqjjm-libcutensor-windows-x86_64-1.5.0.3-archive.zip...
[2023-09-22T02:52:53+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/q7jcksly352yawl1l7yzzf7l376ziwa3-libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz in 14.921977996826172 seconds.
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:52:53+0000][PID242723][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:53+0000][PID242723][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:52:53+0000][PID242723][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.4.0.6-archive.zip
[2023-09-22T02:52:53+0000][PID242723][process_package][DEBUG] SHA256: 4f01a8aac2c25177e928c63381a80e3342f214ec86ad66965dcbfe81fc5c901d
[2023-09-22T02:52:53+0000][PID242723][process_package][DEBUG] MD5: d21e0d5f2bd8c29251ffacaa85f0d733
[2023-09-22T02:52:53+0000][PID242723][process_package][DEBUG] Size: 431385567
[2023-09-22T02:52:53+0000][PID242723][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.4.0.6-archive.zip to the Nix store...
[2023-09-22T02:52:53+0000][PID242723][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.4.0.6-archive.zip to the Nix store in 0.013431549072265625 seconds.
[2023-09-22T02:52:53+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/7j2jppzd7fi00m0hhq7b2jjp363y8i7v-libcutensor-windows-x86_64-1.4.0.6-archive.zip...
[2023-09-22T02:52:54+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/qz1hpcq6nxv0z0n0p1rjdg2ag2kyi7g1-libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz in 14.928367376327515 seconds.
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-22T02:52:54+0000][PID242726][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:52:54+0000][PID242726][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:52:54+0000][PID242726][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz
[2023-09-22T02:52:54+0000][PID242726][process_package][DEBUG] SHA256: 793b425c30ffd423c4f3a2e94acaf4fcb6752264aa73b74695a002dd2fe94b1a
[2023-09-22T02:52:54+0000][PID242726][process_package][DEBUG] MD5: 055271e1e237beb102394a5431684a37
[2023-09-22T02:52:54+0000][PID242726][process_package][DEBUG] Size: 365956196
[2023-09-22T02:52:54+0000][PID242726][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-22T02:52:54+0000][PID242726][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz to the Nix store in 0.01420283317565918 seconds.
[2023-09-22T02:52:54+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/53hp68861qra26fcb8gac7g18lswwbrg-libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz...
[2023-09-22T02:53:02+0000][PID242720][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/1n8xrchy7im8v746vqjjj4s6jqhciv8g-libcutensor-windows-x86_64-1.3.2.3-archive.zip in 8.522124290466309 seconds.
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 3 shared libraries.
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:53:02+0000][PID242720][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:03+0000][PID242721][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/jbs6pjc4z4mn5pa392s84dad5nskysh0-libcutensor-windows-x86_64-1.3.3.2-archive.zip in 10.08148717880249 seconds.
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 2 headers.
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 3 shared libraries.
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:53:03+0000][PID242721][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:04+0000][PID242725][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/66s6g8dx81akm36p1fh8vz4r3m2dqjjm-libcutensor-windows-x86_64-1.5.0.3-archive.zip in 11.305542945861816 seconds.
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-22T02:53:05+0000][PID242725][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:05+0000][PID242724][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/ccl9i73nxn1vp47wq8a5mpnp68khdz2z-libcutensor-windows-x86_64-1.6.0.3-archive.zip in 13.004363059997559 seconds.
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-22T02:53:05+0000][PID242724][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:06+0000][PID242723][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/7j2jppzd7fi00m0hhq7b2jjp363y8i7v-libcutensor-windows-x86_64-1.4.0.6-archive.zip in 12.496239423751831 seconds.
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-22T02:53:06+0000][PID242723][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:12+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/53hp68861qra26fcb8gac7g18lswwbrg-libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz in 18.93325686454773 seconds.
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:53:12+0000][PID242726][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:13+0000][PID242726][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:53:13+0000][PID242726][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:13+0000][PID242726][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:53:13+0000][PID242726][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.1.5-archive.zip
[2023-09-22T02:53:13+0000][PID242726][process_package][DEBUG] SHA256: 36eac790df7b2c7bb4578cb355f1df65d17965ffc9b4f6218d1cdb82f87ab866
[2023-09-22T02:53:13+0000][PID242726][process_package][DEBUG] MD5: 1d5f775c2bbf8e68827a23913e2896bd
[2023-09-22T02:53:13+0000][PID242726][process_package][DEBUG] Size: 690592392
[2023-09-22T02:53:13+0000][PID242726][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.1.5-archive.zip to the Nix store...
[2023-09-22T02:53:13+0000][PID242726][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.1.5-archive.zip to the Nix store in 0.012754201889038086 seconds.
[2023-09-22T02:53:13+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/z7dfb3ydp8c280yqgbk3shxs6adanqi3-libcutensor-windows-x86_64-1.6.1.5-archive.zip...
[2023-09-22T02:53:14+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/gj9hgzj57jvnbh9h2rvqd957366d00k8-libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz in 23.587215185165405 seconds.
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:53:14+0000][PID242722][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:14+0000][PID242722][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:53:14+0000][PID242722][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz
[2023-09-22T02:53:14+0000][PID242722][process_package][DEBUG] SHA256: 0f2745681b1d0556f9f46ff6af4937662793498d7367b5f8f6b8625ac051629e
[2023-09-22T02:53:14+0000][PID242722][process_package][DEBUG] MD5: b84a2f6712e39314f6c54b429152339f
[2023-09-22T02:53:14+0000][PID242722][process_package][DEBUG] Size: 538838404
[2023-09-22T02:53:14+0000][PID242722][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-22T02:53:14+0000][PID242722][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz to the Nix store in 0.012932300567626953 seconds.
[2023-09-22T02:53:14+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/yxam1ah0h3lp7y15kjmj7mghnik2s799-libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz...
[2023-09-22T02:53:14+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/spqx52qx2g7g7gr805870j9csvg6f3h0-libcutensor-linux-sbsa-1.7.0.1-archive.tar.xz in 21.659223318099976 seconds.
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-22T02:53:15+0000][PID242727][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:15+0000][PID242727][process_package][INFO] Architecture: linux-x86_64
[2023-09-22T02:53:15+0000][PID242727][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz
[2023-09-22T02:53:15+0000][PID242727][process_package][DEBUG] SHA256: dd3557891371a19e73e7c955efe5383b0bee954aba6a30e4892b0e7acb9deb26
[2023-09-22T02:53:15+0000][PID242727][process_package][DEBUG] MD5: 7c7e655e2ef1c57ede351f5f5c7c59be
[2023-09-22T02:53:15+0000][PID242727][process_package][DEBUG] Size: 542970468
[2023-09-22T02:53:15+0000][PID242727][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz to the Nix store...
[2023-09-22T02:53:15+0000][PID242727][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz to the Nix store in 0.01211237907409668 seconds.
[2023-09-22T02:53:15+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/wzffa3ih9157qvp25i1awmw9x7zwqgfg-libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz...
[2023-09-22T02:53:21+0000][PID242726][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/z7dfb3ydp8c280yqgbk3shxs6adanqi3-libcutensor-windows-x86_64-1.6.1.5-archive.zip in 8.604988813400269 seconds.
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-22T02:53:21+0000][PID242726][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/10.2'), PosixPath('lib/11.0'), PosixPath('lib/11')}
[2023-09-22T02:53:36+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/yxam1ah0h3lp7y15kjmj7mghnik2s799-libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz in 22.11992573738098 seconds.
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-22T02:53:36+0000][PID242722][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:36+0000][PID242722][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:53:36+0000][PID242722][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.2.3-archive.zip
[2023-09-22T02:53:36+0000][PID242722][process_package][DEBUG] SHA256: 07cb312d7cafc7bb2f33d775e1ef5fffd1703d5c6656e785a7a8f0f01939907e
[2023-09-22T02:53:36+0000][PID242722][process_package][DEBUG] MD5: 5ae1c56bf4d457933dc1acb58a4ac995
[2023-09-22T02:53:36+0000][PID242722][process_package][DEBUG] Size: 1063805254
[2023-09-22T02:53:36+0000][PID242722][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.2.3-archive.zip to the Nix store...
[2023-09-22T02:53:36+0000][PID242722][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.2.3-archive.zip to the Nix store in 0.012377262115478516 seconds.
[2023-09-22T02:53:36+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/kd1n6npcraidqj8yjpyr7iavjchdpgvw-libcutensor-windows-x86_64-1.6.2.3-archive.zip...
[2023-09-22T02:53:37+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/wzffa3ih9157qvp25i1awmw9x7zwqgfg-libcutensor-linux-x86_64-1.7.0.1-archive.tar.xz in 22.307631015777588 seconds.
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-22T02:53:37+0000][PID242727][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:37+0000][PID242727][process_package][INFO] Architecture: windows-x86_64
[2023-09-22T02:53:37+0000][PID242727][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.7.0.1-archive.zip
[2023-09-22T02:53:37+0000][PID242727][process_package][DEBUG] SHA256: cdbb53bcc1c7b20ee0aa2dee781644a324d2d5e8065944039024fe22d6b822ab
[2023-09-22T02:53:37+0000][PID242727][process_package][DEBUG] MD5: 7d20a5823e94074e273525b0713f812b
[2023-09-22T02:53:37+0000][PID242727][process_package][DEBUG] Size: 1070143817
[2023-09-22T02:53:37+0000][PID242727][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.7.0.1-archive.zip to the Nix store...
[2023-09-22T02:53:37+0000][PID242727][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.7.0.1-archive.zip to the Nix store in 0.01220703125 seconds.
[2023-09-22T02:53:37+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/j01j34lbnzj7pgg1prbavxm9l1zrpb42-libcutensor-windows-x86_64-1.7.0.1-archive.zip...
[2023-09-22T02:53:48+0000][PID242722][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/kd1n6npcraidqj8yjpyr7iavjchdpgvw-libcutensor-windows-x86_64-1.6.2.3-archive.zip in 12.04184365272522 seconds.
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 8 shared libraries.
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 16 static libraries.
[2023-09-22T02:53:48+0000][PID242722][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:49+0000][PID242727][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/j01j34lbnzj7pgg1prbavxm9l1zrpb42-libcutensor-windows-x86_64-1.7.0.1-archive.zip in 12.521149158477783 seconds.
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 3 headers.
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 8 shared libraries.
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 16 static libraries.
[2023-09-22T02:53:49+0000][PID242727][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/10.2'), PosixPath('lib/12'), PosixPath('lib/11')}
```

</details>
