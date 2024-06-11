{
  cuda-redist-feature-detector,
  fetchurl,
  jq,
  lib,
  nixVersions,
  pkgs,
  srcOnly,
  writers,
  writeShellApplication,
}:
let
  inherit (lib.attrsets) nameValuePair;
  inherit (lib.modules) evalModules;
  inherit (lib.trivial) importJSON pipe;
  inherit (lib.strings) removeSuffix;

  # This does type-checking for us as well as bringing our data and utils helpers into scope.
  inherit
    ((evalModules {
      specialArgs = {
        inherit pkgs;
      };
      modules = [
        ../../modules
        {
          config.data.indices.sha256AndRelativePath = importJSON ../../modules/data/indices/sha256-and-relative-path.json;
        }
      ];
    }).config
    )
    data
    utils
    ;

  sha256ToUnpackedStorePath = pipe data.indices.sha256AndRelativePath [
    (utils.mapIndexLeavesToList (
      args:
      let
        inherit (args.leaf) sha256;
        tarballSrc = fetchurl {
          inherit sha256;
          url =
            if args.redistName == "tensorrt" then
              utils.mkTensorRTURL args.leaf.relativePath
            else
              utils.mkRedistURL args.redistName (
                utils.mkRelativePath (args // { inherit (args.leaf) relativePath; })
              );
        };
        # Thankfully, using srcOnly is equivalent to using fetchzip!
        unpackedSrc = srcOnly {
          __structuredAttrs = true;
          strictDeps = true;

          preferLocalBuild = true;
          allowSubstitutes = false;

          name = pipe tarballSrc.name [
            (removeSuffix ".tar.xz")
            (removeSuffix ".tar.gz")
          ];
          src = tarballSrc;
        };
      in
      nameValuePair sha256 unpackedSrc
    ))
    builtins.listToAttrs
    # Remove all null values from the result.
    (lib.attrsets.filterAttrsRecursive (_: value: value != null))
    # Write the results to JSON for further processing with JQ.
    (writers.writeJSON "sha256-to-unpacked-store-path.json")
  ];
in
writeShellApplication {
  name = "mk-index-of-package-info";
  runtimeInputs = [
    cuda-redist-feature-detector
    jq
    nixVersions.latest
  ];
  runtimeEnv = {
    JQ_COMMON_FLAGS = [
      "--raw-output"
      "--sort-keys"
    ];
  };
  derivationArgs = {
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  text = ''
    indexOfSha256AndRelativePathJSONPath="./modules/data/indices/sha256-and-relative-path.json"
    indexOfPackageInfoJSONPath="./modules/data/indices/package-info.json"
    hashToUnpackedStorePathJSONPath="${sha256ToUnpackedStorePath}"
    unpackedStorePathToNarHashJSONPath="$(mktemp)"
    unpackedStorePathToFeatureJSONPath="$(mktemp)"

    # Check if the input files exist
    if [[ ! -f "$indexOfSha256AndRelativePathJSONPath" ]]; then
      echo "The input file $indexOfSha256AndRelativePathJSONPath does not exist"
      exit 1
    fi

    if [[ ! -f "$hashToUnpackedStorePathJSONPath" ]]; then
      echo "The input file $hashToUnpackedStorePathJSONPath does not exist"
      exit 1
    fi

    echo "Acquiring NAR hashes for store paths in $hashToUnpackedStorePathJSONPath"
    jq "''${JQ_COMMON_FLAGS[@]}" '.[]' "$hashToUnpackedStorePathJSONPath" \
      | nix path-info --quiet --json --stdin \
      | jq "''${JQ_COMMON_FLAGS[@]}" 'with_entries(.value |= .narHash)' \
      > "$unpackedStorePathToNarHashJSONPath"

    echo "Acquiring features for store paths in $hashToUnpackedStorePathJSONPath"
    jq "''${JQ_COMMON_FLAGS[@]}" '.[]' "$hashToUnpackedStorePathJSONPath" \
      | cuda-redist-feature-detector --stdin \
      > "$unpackedStorePathToFeatureJSONPath"

    echo "Joining the results"
    jq "''${JQ_COMMON_FLAGS[@]}" --from-file "${./filter.jq}" "$indexOfSha256AndRelativePathJSONPath" \
      --slurpfile hashToUnpackedStorePath "$hashToUnpackedStorePathJSONPath" \
      --slurpfile unpackedStorePathToFeature "$unpackedStorePathToFeatureJSONPath" \
      --slurpfile unpackedStorePathToNarHash "$unpackedStorePathToNarHashJSONPath" \
      > "$indexOfPackageInfoJSONPath"

    echo "Cleaning up temporary files"
    rm "$unpackedStorePathToNarHashJSONPath" "$unpackedStorePathToFeatureJSONPath"
  '';
}
