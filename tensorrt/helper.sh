#!/usr/bin/env bash

# Requires nix and jq

set -euo pipefail

mkRelativePath() {
  local -r cudaMajorMinorVersion=${1:?}
  local -r tensorrtMajorMinorPatchBuildVersion=${2:?}
  local -r redistArch=${3:?}

  local -r tensorrtMajorMinorPatchVersion="$(echo "$tensorrtMajorMinorPatchBuildVersion" | cut -d. -f1-3)"

  local archiveDir=""
  local archiveExtension=""
  local osName=""
  local platformName=""
  case "$redistArch" in
  linux-aarch64) archiveDir="tars" && archiveExtension="tar.gz" && osName="l4t" && platformName="aarch64-gnu" ;;
  linux-sbsa) archiveDir="tars" && archiveExtension="tar.gz" && osName="Ubuntu-22.04" && platformName="aarch64-gnu" ;;
  linux-x86_64) archiveDir="tars" && archiveExtension="tar.gz" && osName="Linux" && platformName="x86_64-gnu" ;;
  windows-x86_64) archiveDir="zip" && archiveExtension="zip" && osName="Windows" && platformName="win10" ;;
  *)
    echo "mkRelativePath: Unsupported redistArch: $redistArch" >&2
    exit 1
    ;;
  esac

  # Windows info is different for 10.0.*
  if [[ $tensorrtMajorMinorPatchBuildVersion =~ 10.0.* && $redistArch == "windows-x86_64" ]]; then
    archiveDir="zips"
    osName="Windows10"
  fi

  local -r relativePath="tensorrt/$tensorrtMajorMinorPatchVersion/$archiveDir/TensorRT-${tensorrtMajorMinorPatchBuildVersion}.${osName}.${platformName}.cuda-${cudaMajorMinorVersion}.${archiveExtension}"
  echo "$relativePath"
}

getNixStorePath() {
  local -r relativePath=${1:?}
  local -r jsonBlob="$(nix store prefetch-file --json "https://developer.nvidia.com/downloads/compute/machine-learning/$relativePath")"
  if [[ -z $jsonBlob ]]; then
    echo "getNixStorePath: Failed to fetch jsonBlob for relativePath: $relativePath" >&2
    exit 1
  fi
  local -r storePath="$(echo "$jsonBlob" | jq -cr '.storePath')"
  echo "$storePath"
}

printOutput() {
  local -r cudaMajorMinorVersion=${1:?}
  local -r redistArch=${2:?}
  local -r md5Hash=${3:?}
  local -r relativePath=${4:?}
  local -r sha256Hash=${5:?}
  local -r size=${6:?}

  local -r cudaVariant="cuda$(echo "$cudaMajorMinorVersion" | cut -d. -f1)"

  # Echo everything to stdout using JQ to format the output as JSON
  jq \
    --raw-output \
    --sort-keys \
    --null-input \
    --arg redistArch "$redistArch" \
    --arg cudaVariant "$cudaVariant" \
    --arg md5Hash "$md5Hash" \
    --arg relativePath "$relativePath" \
    --arg sha256Hash "$sha256Hash" \
    --arg size "$size" \
    '{
      $redistArch: {
        $cudaVariant: {
          md5: $md5Hash,
          relative_path: $relativePath,
          sha256: $sha256Hash,
          size: $size
        }
      }
    }'
}

main() {
  local -r cudaMajorMinorVersion=${1:?}
  if [[ ! $cudaMajorMinorVersion =~ ^[0-9]+\.[0-9]+$ ]]; then
    echo "main: Invalid cudaMajorMinorVersion: $cudaMajorMinorVersion" >&2
    exit 1
  fi

  local -r tensorrtMajorMinorPatchBuildVersion=${2:?}
  if [[ ! $tensorrtMajorMinorPatchBuildVersion =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "main: Invalid tensorrtMajorMinorPatchBuildVersion: $tensorrtMajorMinorPatchBuildVersion" >&2
    exit 1
  fi

  local -r redistArch=${3:?}
  case "$redistArch" in
  linux-aarch64) ;;
  linux-sbsa) ;;
  linux-x86_64) ;;
  windows-x86_64) ;;
  *)
    echo "main: Unsupported redistArch: $redistArch" >&2
    exit 1
    ;;
  esac

  local -r relativePath="$(mkRelativePath "$cudaMajorMinorVersion" "$tensorrtMajorMinorPatchBuildVersion" "$redistArch")"
  local -r storePath="$(getNixStorePath "$relativePath")"
  echo "main: storePath: $storePath" >&2
  local -r md5Hash="$(nix hash file --type md5 --base16 "$storePath")"
  local -r sha256Hash="$(nix hash file --type sha256 --base16 "$storePath")"
  local -r size="$(du -b "$storePath" | cut -f1)"

  printOutput "$cudaMajorMinorVersion" "$redistArch" "$md5Hash" "$relativePath" "$sha256Hash" "$size"
}

main "$@"
