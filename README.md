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

There are two commands:

- `download-manifests`: Download manifests from NVIDIA's website.
- `process-manifests`: Process manifests and write JSON files containing the outputs each package should have.

```console
$ nix run .# -- --help
Usage: cuda-redist-find-features [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug  Enable debug logging.  [default: no-debug]
  --help                Show this message and exit.

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
  --debug / --no-debug        Enable debug logging.  [default: no-debug]
  --no-parallel / --parallel  Disable parallel processing.  [default:
                              parallel]
  --min-version VERSION       Minimum version to accept. Exclusive with
                              --version.
  --max-version VERSION       Maximum version to accept. Exclusive with
                              --version.
  --version VERSION           Version to accept. If not specified, operates on
                              all versions. Exclusive with --min-version and
                              --max-version.
  --help                      Show this message and exit.
```

### `process-manifests`

```console
$ nix run .# -- process-manifests --help
Usage: cuda-redist-find-features process-manifests [OPTIONS] URL MANIFEST_DIR

  Retrieves all manifests matching `redistrib_*.json` in MANIFEST_DIR and
  processes them, using URL as the base of for the relative paths in the
  manifest.

  Downloads all packages in the manifest, checks them to see what features
  they provide, and writes a new manifest with this information to
  MANIFEST_DIR.

  URL should not include a trailing slash.

  MANIFEST_DIR should be a directory containing JSON manifest(s).

Options:
  --cleanup / --no-cleanup    Remove files after use.  [default: no-cleanup]
  --debug / --no-debug        Enable debug logging.  [default: no-debug]
  --no-parallel / --parallel  Disable parallel processing.  [default:
                              parallel]
  --min-version VERSION       Minimum version to accept. Exclusive with
                              --version.
  --max-version VERSION       Maximum version to accept. Exclusive with
                              --version.
  --version VERSION           Version to accept. If not specified, operates on
                              all versions. Exclusive with --min-version and
                              --max-version.
  --help                      Show this message and exit.
```

## Examples

### cuTensor

<details><summary>download-manifests</summary>

```console
$ nix run .# -- --debug download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
[2023-09-23T12:47:44+0000][PID72245][_debug_callback][INFO] Debug logging enabled.
[2023-09-23T12:47:44+0000][PID72245][_url_callback][INFO] Using URL https://developer.download.nvidia.com/compute/cutensor/redist.
[2023-09-23T12:47:44+0000][PID72245][_manifest_dir_callback][INFO] Using dir cutensor_manifests.
[2023-09-23T12:47:44+0000][PID72245][from_ref][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-23T12:47:45+0000][PID72245][_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-23T12:47:45+0000][PID72245][_from_url][DEBUG] Searching with regex href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]...
[2023-09-23T12:47:45+0000][PID72245][from_ref][DEBUG] Found 8 manifests in 0.27196645736694336 seconds.
[2023-09-23T12:47:45+0000][PID73858][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.2.json...
[2023-09-23T12:47:45+0000][PID73859][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.3.json...
[2023-09-23T12:47:45+0000][PID73860][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-23T12:47:45+0000][PID73861][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json...
[2023-09-23T12:47:45+0000][PID73862][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json...
[2023-09-23T12:47:45+0000][PID73863][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json...
[2023-09-23T12:47:45+0000][PID73864][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json...
[2023-09-23T12:47:45+0000][PID73865][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.7.0.json...
[2023-09-23T12:47:45+0000][PID73859][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.3.json in 0.043467044830322266 seconds.
[2023-09-23T12:47:45+0000][PID73858][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.3.2.json in 0.0454099178314209 seconds.
[2023-09-23T12:47:45+0000][PID73863][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json in 0.045320987701416016 seconds.
[2023-09-23T12:47:45+0000][PID73861][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json in 0.04874825477600098 seconds.
[2023-09-23T12:47:45+0000][PID73862][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json in 0.04931354522705078 seconds.
[2023-09-23T12:47:45+0000][PID73864][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json in 0.04970574378967285 seconds.
[2023-09-23T12:47:45+0000][PID73860][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.05129528045654297 seconds.
[2023-09-23T12:47:45+0000][PID73865][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.7.0.json in 0.06581258773803711 seconds.
```

</details>

<details><summary>download-manifests with --version</summary>

```console
$ nix run .# -- --debug download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --version 1.4.0
[2023-09-23T12:48:19+0000][PID75617][_debug_callback][INFO] Debug logging enabled.
[2023-09-23T12:48:19+0000][PID75617][_version_callback][INFO] {}
[2023-09-23T12:48:19+0000][PID75617][_version_callback][INFO] Version set to 1.4.0.
[2023-09-23T12:48:19+0000][PID75617][_url_callback][INFO] Using URL https://developer.download.nvidia.com/compute/cutensor/redist.
[2023-09-23T12:48:19+0000][PID75617][_manifest_dir_callback][INFO] Using dir cutensor_manifests.
[2023-09-23T12:48:19+0000][PID75617][from_ref][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-23T12:48:19+0000][PID75617][_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-23T12:48:19+0000][PID75617][_from_url][DEBUG] Searching with regex href=['"]redistrib_(1\.4\.0)\.json['"]...
[2023-09-23T12:48:19+0000][PID75617][from_ref][DEBUG] Found 1 manifests in 0.2374415397644043 seconds.
[2023-09-23T12:48:19+0000][PID77230][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-23T12:48:19+0000][PID77230][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.054283857345581055 seconds.
```

</details>

<details><summary>download-manifests with --min-version and --max-version</summary>

```console
$ nix run .# -- --debug download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --min-version 1.4.0 --max-version 1.6.2
warning: Git tree '/home/connorbaker/cuda-redist-find-features' is dirty
[2023-09-23T12:48:50+0000][PID77363][_debug_callback][INFO] Debug logging enabled.
[2023-09-23T12:48:50+0000][PID77363][_min_version_callback][INFO] Minimum version set to 1.4.0.
[2023-09-23T12:48:50+0000][PID77363][_max_version_callback][INFO] Maximum version set to 1.6.2.
[2023-09-23T12:48:50+0000][PID77363][_url_callback][INFO] Using URL https://developer.download.nvidia.com/compute/cutensor/redist.
[2023-09-23T12:48:50+0000][PID77363][_manifest_dir_callback][INFO] Using dir cutensor_manifests.
[2023-09-23T12:48:50+0000][PID77363][from_ref][DEBUG] Fetching manifests from https://developer.download.nvidia.com/compute/cutensor/redist...
[2023-09-23T12:48:50+0000][PID77363][_from_url][DEBUG] Fetched https://developer.download.nvidia.com/compute/cutensor/redist successfully.
[2023-09-23T12:48:50+0000][PID77363][_from_url][DEBUG] Searching with regex href=[\'"]redistrib_(\d+\.\d+\.\d+(?:.\d+)?)\.json[\'"]...
[2023-09-23T12:48:50+0000][PID77363][_from_url][DEBUG] Skipping 1.3.2 because version 1.3.2 is not between 1.4.0 and 1.6.2
[2023-09-23T12:48:50+0000][PID77363][_from_url][DEBUG] Skipping 1.3.3 because version 1.3.3 is not between 1.4.0 and 1.6.2
[2023-09-23T12:48:50+0000][PID77363][_from_url][DEBUG] Skipping 1.7.0 because version 1.7.0 is not between 1.4.0 and 1.6.2
[2023-09-23T12:48:50+0000][PID77363][from_ref][DEBUG] Found 5 manifests in 0.23999786376953125 seconds.
[2023-09-23T12:48:50+0000][PID78976][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json...
[2023-09-23T12:48:50+0000][PID78977][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json...
[2023-09-23T12:48:50+0000][PID78978][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json...
[2023-09-23T12:48:50+0000][PID78979][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json...
[2023-09-23T12:48:50+0000][PID78980][read_bytes][DEBUG] Reading manifest from https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json...
[2023-09-23T12:48:50+0000][PID78976][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.4.0.json in 0.04159855842590332 seconds.
[2023-09-23T12:48:50+0000][PID78979][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.1.json in 0.04214191436767578 seconds.
[2023-09-23T12:48:50+0000][PID78980][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.2.json in 0.04859662055969238 seconds.
[2023-09-23T12:48:50+0000][PID78977][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.5.0.json in 0.053003787994384766 seconds.
[2023-09-23T12:48:50+0000][PID78978][read_bytes][DEBUG] Read https://developer.download.nvidia.com/compute/cutensor/redist/redistrib_1.6.0.json in 0.05305337905883789 seconds.
```

</details>

<details><summary>process-manifests</summary>

Assuming

```console
nix run .# -- --debug download-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests --min-version 1.4.0 --max-version 1.6.2
```

was run previously,

```console
$ nix run .# -- --debug process-manifests https://developer.download.nvidia.com/compute/cutensor/redist cutensor_manifests
[2023-09-23T12:50:07+0000][PID80910][_debug_callback][INFO] Debug logging enabled.
[2023-09-23T12:50:07+0000][PID80910][_url_callback][INFO] Using URL https://developer.download.nvidia.com/compute/cutensor/redist.
[2023-09-23T12:50:07+0000][PID80910][_manifest_dir_callback][INFO] Using dir cutensor_manifests.
[2023-09-23T12:50:07+0000][PID80910][from_ref][DEBUG] Fetching manifests from cutensor_manifests...
[2023-09-23T12:50:07+0000][PID80910][_from_dir][DEBUG] Globbing for redistrib_[0123456789]*.json...
[2023-09-23T12:50:07+0000][PID80910][from_ref][DEBUG] Found 5 manifests in 0.008830070495605469 seconds.
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.2.json...
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.2.json in 2.002716064453125e-05 seconds.
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.2.json
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Version: 1.6.2
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Release date: 2022-12-12
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.4.0.json...
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.4.0.json in 2.2411346435546875e-05 seconds.
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.4.0.json
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Version: 1.4.0
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Release date: 2021-11-19
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.0.json...
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.0.json in 1.0728836059570312e-05 seconds.
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.0.json
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Version: 1.6.0
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Release date: 2022-06-24
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.5.0.json...
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.5.0.json in 9.059906005859375e-06 seconds.
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.5.0.json
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Version: 1.5.0
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Release date: 2022-03-08
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Reading manifest from cutensor_manifests/redistrib_1.6.1.json...
[2023-09-23T12:50:07+0000][PID80910][read_bytes][DEBUG] Read cutensor_manifests/redistrib_1.6.1.json in 8.344650268554688e-06 seconds.
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Loaded manifest: cutensor_manifests/redistrib_1.6.1.json
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Version: 1.6.1
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][INFO] Release date: 2022-10-05
[2023-09-23T12:50:07+0000][PID80910][parse_manifest][DEBUG] Manifest keys: dict_keys(['libcutensor'])
[2023-09-23T12:50:07+0000][PID80922][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-23T12:50:07+0000][PID80922][process_package][DEBUG] License: cuTensor
[2023-09-23T12:50:07+0000][PID80922][process_package][INFO] Version: 1.6.2.3
[2023-09-23T12:50:07+0000][PID80922][process_package][INFO] Architecture: linux-ppc64le
[2023-09-23T12:50:07+0000][PID80922][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz
[2023-09-23T12:50:07+0000][PID80922][process_package][DEBUG] SHA256: 558329fa05409f914ebbe218a1cf7c9ccffdb7aa2642b96db85fd78b5ad534d1
[2023-09-23T12:50:07+0000][PID80923][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-23T12:50:07+0000][PID80922][process_package][DEBUG] MD5: 8d5d129aa7863312a95084ab5a27b7e7
[2023-09-23T12:50:07+0000][PID80922][process_package][DEBUG] Size: 535585612
[2023-09-23T12:50:07+0000][PID80923][process_package][DEBUG] License: cuTensor
[2023-09-23T12:50:07+0000][PID80924][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-23T12:50:07+0000][PID80922][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:07+0000][PID80923][process_package][INFO] Version: 1.4.0.6
[2023-09-23T12:50:07+0000][PID80924][process_package][DEBUG] License: cuTensor
[2023-09-23T12:50:07+0000][PID80925][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-23T12:50:07+0000][PID80924][process_package][INFO] Version: 1.6.0.3
[2023-09-23T12:50:07+0000][PID80925][process_package][DEBUG] License: cuTensor
[2023-09-23T12:50:07+0000][PID80923][process_package][INFO] Architecture: linux-ppc64le
[2023-09-23T12:50:07+0000][PID80923][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz
[2023-09-23T12:50:07+0000][PID80925][process_package][INFO] Version: 1.5.0.3
[2023-09-23T12:50:07+0000][PID80926][process_package][INFO] Package: NVIDIA cuTENSOR
[2023-09-23T12:50:07+0000][PID80923][process_package][DEBUG] SHA256: 5da44ff2562ab7b9286122653e54f28d2222c8aab4bb02e9bdd4cf7e4b7809be
[2023-09-23T12:50:07+0000][PID80924][process_package][INFO] Architecture: linux-ppc64le
[2023-09-23T12:50:07+0000][PID80923][process_package][DEBUG] MD5: 6058c728485072c980f652c2de38b016
[2023-09-23T12:50:07+0000][PID80924][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz
[2023-09-23T12:50:07+0000][PID80926][process_package][DEBUG] License: cuTensor
[2023-09-23T12:50:07+0000][PID80923][process_package][DEBUG] Size: 218951992
[2023-09-23T12:50:07+0000][PID80924][process_package][DEBUG] SHA256: 6af9563a3581e1879dd17e9bae79ceae1b4084f45e735780125aab86056646eb
[2023-09-23T12:50:07+0000][PID80926][process_package][INFO] Version: 1.6.1.5
[2023-09-23T12:50:07+0000][PID80925][process_package][INFO] Architecture: linux-ppc64le
[2023-09-23T12:50:07+0000][PID80924][process_package][DEBUG] MD5: 38e3cd74fb7c0fa9c0836a9d172b9737
[2023-09-23T12:50:07+0000][PID80923][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-23T12:50:07+0000][PID80925][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz
[2023-09-23T12:50:07+0000][PID80924][process_package][DEBUG] Size: 332890432
[2023-09-23T12:50:07+0000][PID80925][process_package][DEBUG] SHA256: ad736acc94e88673b04a3156d7d3a408937cac32d083acdfbd8435582cbe15db
[2023-09-23T12:50:07+0000][PID80924][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:07+0000][PID80925][process_package][DEBUG] MD5: bcdafb6d493aceebfb9a420880f1486c
[2023-09-23T12:50:07+0000][PID80925][process_package][DEBUG] Size: 208384668
[2023-09-23T12:50:07+0000][PID80926][process_package][INFO] Architecture: linux-ppc64le
[2023-09-23T12:50:07+0000][PID80925][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:07+0000][PID80926][process_package][DEBUG] Relative path: libcutensor/linux-ppc64le/libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz
[2023-09-23T12:50:07+0000][PID80926][process_package][DEBUG] SHA256: e895476ab13c4a28bdf018f23299746968564024783c066a2602bc0f09b86e47
[2023-09-23T12:50:07+0000][PID80926][process_package][DEBUG] MD5: c44194d2067ce296f9a2c51ddbd6eb7b
[2023-09-23T12:50:07+0000][PID80926][process_package][DEBUG] Size: 365411216
[2023-09-23T12:50:07+0000][PID80926][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-23T12:50:07+0000][PID80925][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz to the Nix store in 0.012704610824584961 seconds.
[2023-09-23T12:50:07+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/9fy3afhldjlgigyc09348nc50ccr7kq1-libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz...
[2023-09-23T12:50:07+0000][PID80922][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz to the Nix store in 0.014284849166870117 seconds.
[2023-09-23T12:50:07+0000][PID80923][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz to the Nix store in 0.014307022094726562 seconds.
[2023-09-23T12:50:07+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/8gvv8lyz2qcjasxvxbq6mi3na8j4ncf1-libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz...
[2023-09-23T12:50:07+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/5b7bmhi1l35i6kqx6rwxq2hxiicshkh4-libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz...
[2023-09-23T12:50:07+0000][PID80924][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz to the Nix store in 0.021808862686157227 seconds.
[2023-09-23T12:50:07+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/897fvwmby7nc9ii3adshfn7f2f671bbs-libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz...
[2023-09-23T12:50:07+0000][PID80926][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz to the Nix store in 0.02199530601501465 seconds.
[2023-09-23T12:50:07+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/mcdm0ifn6lwnbrqskki5jnvrzs07vkpb-libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz...
[2023-09-23T12:50:16+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/9fy3afhldjlgigyc09348nc50ccr7kq1-libcutensor-linux-ppc64le-1.5.0.3-archive.tar.xz in 8.962098360061646 seconds.
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:16+0000][PID80925][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:16+0000][PID80925][process_package][INFO] Architecture: linux-sbsa
[2023-09-23T12:50:16+0000][PID80925][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz
[2023-09-23T12:50:16+0000][PID80925][process_package][DEBUG] SHA256: 5b9ac479b1dadaf40464ff3076e45f2ec92581c07df1258a155b5bcd142f6090
[2023-09-23T12:50:16+0000][PID80925][process_package][DEBUG] MD5: 62149d726480d12c9a953d27edc208dc
[2023-09-23T12:50:16+0000][PID80925][process_package][DEBUG] Size: 156512748
[2023-09-23T12:50:16+0000][PID80925][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:16+0000][PID80925][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz to the Nix store in 0.012617349624633789 seconds.
[2023-09-23T12:50:16+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/5vb91ij9n4rbc0zj6118flzbx1dp3n8j-libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz...
[2023-09-23T12:50:16+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/5b7bmhi1l35i6kqx6rwxq2hxiicshkh4-libcutensor-linux-ppc64le-1.4.0.6-archive.tar.xz in 9.456808805465698 seconds.
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:16+0000][PID80923][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:16+0000][PID80923][process_package][INFO] Architecture: linux-sbsa
[2023-09-23T12:50:16+0000][PID80923][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz
[2023-09-23T12:50:16+0000][PID80923][process_package][DEBUG] SHA256: 6b06d63a5bc49c1660be8c307795f8a901c93dcde7b064455a6c81333c7327f4
[2023-09-23T12:50:16+0000][PID80923][process_package][DEBUG] MD5: a6f3fd515c052df43fbee9508ea87e1e
[2023-09-23T12:50:16+0000][PID80923][process_package][DEBUG] Size: 163596044
[2023-09-23T12:50:16+0000][PID80923][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-23T12:50:16+0000][PID80923][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz to the Nix store in 0.012842893600463867 seconds.
[2023-09-23T12:50:16+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/jkzvn343kkanvldzp0apz0570zi766xg-libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz...
[2023-09-23T12:50:22+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/897fvwmby7nc9ii3adshfn7f2f671bbs-libcutensor-linux-ppc64le-1.6.0.3-archive.tar.xz in 14.989858865737915 seconds.
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:22+0000][PID80924][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:22+0000][PID80924][process_package][INFO] Architecture: linux-sbsa
[2023-09-23T12:50:22+0000][PID80924][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz
[2023-09-23T12:50:22+0000][PID80924][process_package][DEBUG] SHA256: 802f030de069e7eeec2e72f151471fc9776f0272a81804690c749373505dcb70
[2023-09-23T12:50:22+0000][PID80924][process_package][DEBUG] MD5: 38436011c8375ba78e2cd8c47182c6de
[2023-09-23T12:50:22+0000][PID80924][process_package][DEBUG] Size: 253328216
[2023-09-23T12:50:22+0000][PID80924][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:22+0000][PID80924][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz to the Nix store in 0.012593746185302734 seconds.
[2023-09-23T12:50:22+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/0fldgjlk64r6yfs383ra9kmqqhydjyxx-libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz...
[2023-09-23T12:50:22+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/5vb91ij9n4rbc0zj6118flzbx1dp3n8j-libcutensor-linux-sbsa-1.5.0.3-archive.tar.xz in 6.402736186981201 seconds.
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-23T12:50:22+0000][PID80925][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:22+0000][PID80925][process_package][INFO] Architecture: linux-x86_64
[2023-09-23T12:50:22+0000][PID80925][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz
[2023-09-23T12:50:22+0000][PID80925][process_package][DEBUG] SHA256: 4fdebe94f0ba3933a422cff3dd05a0ef7a18552ca274dd12564056993f55471d
[2023-09-23T12:50:22+0000][PID80925][process_package][DEBUG] MD5: 7e1b1a613b819d6cf6ee7fbc70f16105
[2023-09-23T12:50:22+0000][PID80925][process_package][DEBUG] Size: 208925360
[2023-09-23T12:50:22+0000][PID80925][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:22+0000][PID80925][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz to the Nix store in 0.012709379196166992 seconds.
[2023-09-23T12:50:22+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/k5xq37i1j3w710ppy8v0qqg91pkdxflc-libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz...
[2023-09-23T12:50:23+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/mcdm0ifn6lwnbrqskki5jnvrzs07vkpb-libcutensor-linux-ppc64le-1.6.1.5-archive.tar.xz in 16.33398127555847 seconds.
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:23+0000][PID80926][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:23+0000][PID80926][process_package][INFO] Architecture: linux-sbsa
[2023-09-23T12:50:23+0000][PID80926][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz
[2023-09-23T12:50:23+0000][PID80926][process_package][DEBUG] SHA256: f0644bbdca81b890056a7b92714e787333b06a4bd384e4dfbdc3938fbd132e65
[2023-09-23T12:50:23+0000][PID80926][process_package][DEBUG] MD5: a1c841dd532e7aef6963452439042f09
[2023-09-23T12:50:23+0000][PID80926][process_package][DEBUG] Size: 288691268
[2023-09-23T12:50:23+0000][PID80926][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-23T12:50:23+0000][PID80926][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz to the Nix store in 0.012618303298950195 seconds.
[2023-09-23T12:50:23+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/qz1hpcq6nxv0z0n0p1rjdg2ag2kyi7g1-libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz...
[2023-09-23T12:50:24+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/jkzvn343kkanvldzp0apz0570zi766xg-libcutensor-linux-sbsa-1.4.0.6-archive.tar.xz in 7.374499559402466 seconds.
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-23T12:50:24+0000][PID80923][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:24+0000][PID80923][process_package][INFO] Architecture: linux-x86_64
[2023-09-23T12:50:24+0000][PID80923][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz
[2023-09-23T12:50:24+0000][PID80923][process_package][DEBUG] SHA256: 467ba189195fcc4b868334fc16a0ae1e51574139605975cc8004cedebf595964
[2023-09-23T12:50:24+0000][PID80923][process_package][DEBUG] MD5: 5d4009390be0226fc3ee75d225053123
[2023-09-23T12:50:24+0000][PID80923][process_package][DEBUG] Size: 218277136
[2023-09-23T12:50:24+0000][PID80923][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz to the Nix store...
[2023-09-23T12:50:24+0000][PID80923][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz to the Nix store in 0.012694358825683594 seconds.
[2023-09-23T12:50:24+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/q7jcksly352yawl1l7yzzf7l376ziwa3-libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz...
[2023-09-23T12:50:29+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/8gvv8lyz2qcjasxvxbq6mi3na8j4ncf1-libcutensor-linux-ppc64le-1.6.2.3-archive.tar.xz in 22.20299482345581 seconds.
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-23T12:50:29+0000][PID80922][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:29+0000][PID80922][process_package][INFO] Architecture: linux-sbsa
[2023-09-23T12:50:29+0000][PID80922][process_package][DEBUG] Relative path: libcutensor/linux-sbsa/libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz
[2023-09-23T12:50:29+0000][PID80922][process_package][DEBUG] SHA256: 7d4d9088c892bb692ffd70750b49625d1ccbb85390f6eb7c70d6cf582df6d935
[2023-09-23T12:50:29+0000][PID80922][process_package][DEBUG] MD5: f6e0cce3a3b38ced736e55a19da587a3
[2023-09-23T12:50:29+0000][PID80922][process_package][DEBUG] Size: 450705724
[2023-09-23T12:50:29+0000][PID80922][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:29+0000][PID80922][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz to the Nix store in 0.012618541717529297 seconds.
[2023-09-23T12:50:29+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/gj9hgzj57jvnbh9h2rvqd957366d00k8-libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz...
[2023-09-23T12:50:32+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/k5xq37i1j3w710ppy8v0qqg91pkdxflc-libcutensor-linux-x86_64-1.5.0.3-archive.tar.xz in 9.201037406921387 seconds.
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:32+0000][PID80925][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:32+0000][PID80925][process_package][INFO] Architecture: windows-x86_64
[2023-09-23T12:50:32+0000][PID80925][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.5.0.3-archive.zip
[2023-09-23T12:50:32+0000][PID80925][process_package][DEBUG] SHA256: de76f7d92600dda87a14ac756e9d0b5733cbceb88bcd20b3935a82c99342e6cd
[2023-09-23T12:50:32+0000][PID80925][process_package][DEBUG] MD5: 66feef08de8c7fccf7269383e663fd06
[2023-09-23T12:50:32+0000][PID80925][process_package][DEBUG] Size: 421810766
[2023-09-23T12:50:32+0000][PID80925][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.5.0.3-archive.zip to the Nix store...
[2023-09-23T12:50:32+0000][PID80925][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.5.0.3-archive.zip to the Nix store in 0.012717723846435547 seconds.
[2023-09-23T12:50:32+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/66s6g8dx81akm36p1fh8vz4r3m2dqjjm-libcutensor-windows-x86_64-1.5.0.3-archive.zip...
[2023-09-23T12:50:33+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/0fldgjlk64r6yfs383ra9kmqqhydjyxx-libcutensor-linux-sbsa-1.6.0.3-archive.tar.xz in 11.071857452392578 seconds.
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-23T12:50:33+0000][PID80924][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:33+0000][PID80924][process_package][INFO] Architecture: linux-x86_64
[2023-09-23T12:50:33+0000][PID80924][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz
[2023-09-23T12:50:33+0000][PID80924][process_package][DEBUG] SHA256: b07e32a37eee1df7d9330e6d7faf9baf7fffd58007e2544164ea30aec49a5281
[2023-09-23T12:50:33+0000][PID80924][process_package][DEBUG] MD5: 80ffc765748952385d3dbbaef262d72e
[2023-09-23T12:50:33+0000][PID80924][process_package][DEBUG] Size: 333834656
[2023-09-23T12:50:33+0000][PID80924][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:33+0000][PID80924][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz to the Nix store in 0.012582063674926758 seconds.
[2023-09-23T12:50:33+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/gyzp5pspbipp9nmn0sqdl05b01br1rl2-libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz...
[2023-09-23T12:50:33+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/q7jcksly352yawl1l7yzzf7l376ziwa3-libcutensor-linux-x86_64-1.4.0.6-archive.tar.xz in 9.351867437362671 seconds.
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:33+0000][PID80923][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:33+0000][PID80923][process_package][INFO] Architecture: windows-x86_64
[2023-09-23T12:50:33+0000][PID80923][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.4.0.6-archive.zip
[2023-09-23T12:50:33+0000][PID80923][process_package][DEBUG] SHA256: 4f01a8aac2c25177e928c63381a80e3342f214ec86ad66965dcbfe81fc5c901d
[2023-09-23T12:50:33+0000][PID80923][process_package][DEBUG] MD5: d21e0d5f2bd8c29251ffacaa85f0d733
[2023-09-23T12:50:33+0000][PID80923][process_package][DEBUG] Size: 431385567
[2023-09-23T12:50:33+0000][PID80923][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.4.0.6-archive.zip to the Nix store...
[2023-09-23T12:50:33+0000][PID80923][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.4.0.6-archive.zip to the Nix store in 0.01291203498840332 seconds.
[2023-09-23T12:50:33+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/7j2jppzd7fi00m0hhq7b2jjp363y8i7v-libcutensor-windows-x86_64-1.4.0.6-archive.zip...
[2023-09-23T12:50:36+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/qz1hpcq6nxv0z0n0p1rjdg2ag2kyi7g1-libcutensor-linux-sbsa-1.6.1.5-archive.tar.xz in 12.902031898498535 seconds.
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 12 shared libraries.
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 2 shared library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 4 static libraries.
[2023-09-23T12:50:36+0000][PID80926][get_release_features][DEBUG] Found 2 static library directories: {PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:36+0000][PID80926][process_package][INFO] Architecture: linux-x86_64
[2023-09-23T12:50:36+0000][PID80926][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz
[2023-09-23T12:50:36+0000][PID80926][process_package][DEBUG] SHA256: 793b425c30ffd423c4f3a2e94acaf4fcb6752264aa73b74695a002dd2fe94b1a
[2023-09-23T12:50:36+0000][PID80926][process_package][DEBUG] MD5: 055271e1e237beb102394a5431684a37
[2023-09-23T12:50:36+0000][PID80926][process_package][DEBUG] Size: 365956196
[2023-09-23T12:50:36+0000][PID80926][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz to the Nix store...
[2023-09-23T12:50:36+0000][PID80926][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz to the Nix store in 0.012847423553466797 seconds.
[2023-09-23T12:50:36+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/53hp68861qra26fcb8gac7g18lswwbrg-libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz...
[2023-09-23T12:50:37+0000][PID80925][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/66s6g8dx81akm36p1fh8vz4r3m2dqjjm-libcutensor-windows-x86_64-1.5.0.3-archive.zip in 5.652210712432861 seconds.
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-23T12:50:37+0000][PID80925][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:40+0000][PID80923][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/7j2jppzd7fi00m0hhq7b2jjp363y8i7v-libcutensor-windows-x86_64-1.4.0.6-archive.zip in 7.214331865310669 seconds.
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-23T12:50:40+0000][PID80923][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:47+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/gyzp5pspbipp9nmn0sqdl05b01br1rl2-libcutensor-linux-x86_64-1.6.0.3-archive.tar.xz in 13.815793514251709 seconds.
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:47+0000][PID80924][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:47+0000][PID80924][process_package][INFO] Architecture: windows-x86_64
[2023-09-23T12:50:47+0000][PID80924][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.0.3-archive.zip
[2023-09-23T12:50:47+0000][PID80924][process_package][DEBUG] SHA256: e8875e43d8c4169dc65095cb81c5d1e4120f664b4e2288658d73a4a2c2558f3c
[2023-09-23T12:50:47+0000][PID80924][process_package][DEBUG] MD5: 4c76fb8d24296d644033bc992e4159e4
[2023-09-23T12:50:47+0000][PID80924][process_package][DEBUG] Size: 624418613
[2023-09-23T12:50:47+0000][PID80924][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.0.3-archive.zip to the Nix store...
[2023-09-23T12:50:47+0000][PID80924][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.0.3-archive.zip to the Nix store in 0.012735128402709961 seconds.
[2023-09-23T12:50:47+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/ccl9i73nxn1vp47wq8a5mpnp68khdz2z-libcutensor-windows-x86_64-1.6.0.3-archive.zip...
[2023-09-23T12:50:47+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/gj9hgzj57jvnbh9h2rvqd957366d00k8-libcutensor-linux-sbsa-1.6.2.3-archive.tar.xz in 18.306556701660156 seconds.
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/12'), PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:47+0000][PID80922][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/12'), PosixPath('lib/11'), PosixPath('lib/11.0')}
[2023-09-23T12:50:47+0000][PID80922][process_package][INFO] Architecture: linux-x86_64
[2023-09-23T12:50:47+0000][PID80922][process_package][DEBUG] Relative path: libcutensor/linux-x86_64/libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz
[2023-09-23T12:50:47+0000][PID80922][process_package][DEBUG] SHA256: 0f2745681b1d0556f9f46ff6af4937662793498d7367b5f8f6b8625ac051629e
[2023-09-23T12:50:47+0000][PID80922][process_package][DEBUG] MD5: b84a2f6712e39314f6c54b429152339f
[2023-09-23T12:50:47+0000][PID80922][process_package][DEBUG] Size: 538838404
[2023-09-23T12:50:47+0000][PID80922][nix_store_prefetch_file][DEBUG] Adding libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz to the Nix store...
[2023-09-23T12:50:47+0000][PID80922][nix_store_prefetch_file][DEBUG] Added libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz to the Nix store in 0.012361764907836914 seconds.
[2023-09-23T12:50:47+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/yxam1ah0h3lp7y15kjmj7mghnik2s799-libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz...
[2023-09-23T12:50:52+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/53hp68861qra26fcb8gac7g18lswwbrg-libcutensor-linux-x86_64-1.6.1.5-archive.tar.xz in 15.50687289237976 seconds.
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 18 shared libraries.
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 6 static libraries.
[2023-09-23T12:50:52+0000][PID80926][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:52+0000][PID80926][process_package][INFO] Architecture: windows-x86_64
[2023-09-23T12:50:52+0000][PID80926][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.1.5-archive.zip
[2023-09-23T12:50:52+0000][PID80926][process_package][DEBUG] SHA256: 36eac790df7b2c7bb4578cb355f1df65d17965ffc9b4f6218d1cdb82f87ab866
[2023-09-23T12:50:52+0000][PID80926][process_package][DEBUG] MD5: 1d5f775c2bbf8e68827a23913e2896bd
[2023-09-23T12:50:52+0000][PID80926][process_package][DEBUG] Size: 690592392
[2023-09-23T12:50:52+0000][PID80926][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.1.5-archive.zip to the Nix store...
[2023-09-23T12:50:52+0000][PID80926][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.1.5-archive.zip to the Nix store in 0.012521982192993164 seconds.
[2023-09-23T12:50:52+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/z7dfb3ydp8c280yqgbk3shxs6adanqi3-libcutensor-windows-x86_64-1.6.1.5-archive.zip...
[2023-09-23T12:50:54+0000][PID80924][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/ccl9i73nxn1vp47wq8a5mpnp68khdz2z-libcutensor-windows-x86_64-1.6.0.3-archive.zip in 7.07690167427063 seconds.
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-23T12:50:54+0000][PID80924][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:59+0000][PID80926][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/z7dfb3ydp8c280yqgbk3shxs6adanqi3-libcutensor-windows-x86_64-1.6.1.5-archive.zip in 7.707667589187622 seconds.
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 6 shared libraries.
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 3 shared library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 12 static libraries.
[2023-09-23T12:50:59+0000][PID80926][get_release_features][DEBUG] Found 3 static library directories: {PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:51:09+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/yxam1ah0h3lp7y15kjmj7mghnik2s799-libcutensor-linux-x86_64-1.6.2.3-archive.tar.xz in 21.921855211257935 seconds.
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 24 shared libraries.
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 8 static libraries.
[2023-09-23T12:51:09+0000][PID80922][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:51:09+0000][PID80922][process_package][INFO] Architecture: windows-x86_64
[2023-09-23T12:51:09+0000][PID80922][process_package][DEBUG] Relative path: libcutensor/windows-x86_64/libcutensor-windows-x86_64-1.6.2.3-archive.zip
[2023-09-23T12:51:09+0000][PID80922][process_package][DEBUG] SHA256: 07cb312d7cafc7bb2f33d775e1ef5fffd1703d5c6656e785a7a8f0f01939907e
[2023-09-23T12:51:09+0000][PID80922][process_package][DEBUG] MD5: 5ae1c56bf4d457933dc1acb58a4ac995
[2023-09-23T12:51:09+0000][PID80922][process_package][DEBUG] Size: 1063805254
[2023-09-23T12:51:09+0000][PID80922][nix_store_prefetch_file][DEBUG] Adding libcutensor-windows-x86_64-1.6.2.3-archive.zip to the Nix store...
[2023-09-23T12:51:09+0000][PID80922][nix_store_prefetch_file][DEBUG] Added libcutensor-windows-x86_64-1.6.2.3-archive.zip to the Nix store in 0.012323379516601562 seconds.
[2023-09-23T12:51:09+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacking /nix/store/kd1n6npcraidqj8yjpyr7iavjchdpgvw-libcutensor-windows-x86_64-1.6.2.3-archive.zip...
[2023-09-23T12:51:21+0000][PID80922][nix_store_unpack_archive][DEBUG] Unpacked /nix/store/kd1n6npcraidqj8yjpyr7iavjchdpgvw-libcutensor-windows-x86_64-1.6.2.3-archive.zip in 11.895700216293335 seconds.
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found roots: ['include', 'lib']
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found lib directory, checking for libraries.
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 3 headers.
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 2 header directories: {PosixPath('include/cutensor'), PosixPath('include')}
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 8 shared libraries.
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 4 shared library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 16 static libraries.
[2023-09-23T12:51:21+0000][PID80922][get_release_features][DEBUG] Found 4 static library directories: {PosixPath('lib/12'), PosixPath('lib/11.0'), PosixPath('lib/11'), PosixPath('lib/10.2')}
```

</details>
