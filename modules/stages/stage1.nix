{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.attrsets) nameValuePair;
  inherit (lib.options) mkOption;
  inherit (lib.strings) removeSuffix;
  inherit (lib.trivial) pipe;
  inherit (pkgs)
    runCommand
    fetchurl
    srcOnly
    writers
    nixVersions
    jq
    ;
in
{
  imports = [ ./stage0.nix ];
  config.stages = {
    # NOTE: We must use path-interpolation because string interpolation for paths is forbidden in pure evaluation mode.
    stage0.result = lib.trivial.importJSON ../../${config.stages.stage0.outputPath};
    stage1 = {
      description = "Replace the hashes of the tarballs in the index with recursive NAR hashes of the unpacked tarballs.";
      name = "stage1-generate-index-of-nar-hashes";
    };
  };
  options.stages.stage1.result = mkOption {
    description = "Index of recursive NAR hash of unpacked tarballs.";
    type = config.types.indexOf config.types.sriHash;
    default =
      let
        packedHashToUnpackedSrcOutPathJSON = pipe config.stages.stage0.result [
          (config.utils.mapIndexLeavesToList (
            args@{ leaf, redistName, ... }:
            let
              hash = leaf;
              tarballSrc = fetchurl {
                inherit hash;
                url = config.utils.mkRedistURL redistName (config.utils.mkRelativePath args);
              };
              # Thankfully, using srcOnly is equivalent to using fetchzip!
              unpackedSrc = srcOnly {
                __contentAddressed = true;
                __structuredAttrs = true;
                strictDeps = true;

                preferLocalBuild = true;
                allowSubstitutes = false;

                name = removeSuffix ".tar.xz" tarballSrc.name;
                src = tarballSrc;
              };
            in
            nameValuePair hash unpackedSrc.outPath
          ))
          builtins.listToAttrs
          (writers.writeJSON "packed-hash-to-unpacked-src-out-path.json")
        ];

        # Acccumulate and use all of the packages from the previous definition.
        # Forces a bottle-neck in Nix evaluation to ensure that the previous definition is evaluated.
        aggregateUnpackedSrcOutPathToNarHash =
          runCommand "generate-aggregate-unpacked-src-out-path-to-nar-hash"
            {
              __contentAddressed = true;
              __structuredAttrs = true;
              strictDeps = true;

              preferLocalBuild = true;
              allowSubstitutes = false;
              # TODO: Must include requiredSystemFeatures here otherwise the build will error.
              requiredSystemFeatures = [ "recursive-nix" ];

              nativeBuildInputs = [
                jq
                nixVersions.unstable
              ];

              JQ_COMMON_FLAGS = [
                "--compact-output"
                "--sort-keys"
                "--raw-output"
              ];
              env.NIX_CONFIG = builtins.concatStringsSep "\n" [ "extra-experimental-features = nix-command" ];
            }
            (
              # Declare our variables here
              ''
                local packedHashToUnpackedSrcOutPathJSONPath="${packedHashToUnpackedSrcOutPathJSON}"
                local unpackedSrcOutPathToNarHashJSONPath="aggregate-unpacked-src-to-nar-hash.json"
              ''
              # Get the NAR hashes for the store paths
              + ''
                echo "Acquiring NAR hashes for store paths in $packedHashToUnpackedSrcOutPathJSONPath"
                jq "''${JQ_COMMON_FLAGS[@]}" '.[]' "$packedHashToUnpackedSrcOutPathJSONPath" \
                  | nix path-info --quiet --json --stdin \
                  | jq "''${JQ_COMMON_FLAGS[@]}" 'with_entries(.value |= .narHash)' \
                  > "$unpackedSrcOutPathToNarHashJSONPath"
              ''
              # Compose the hash to store path and store path to nar hash mappings
              # We do this partly because we cannot have strings which are store paths in the output!
              + ''
                echo "Composing the hash to store path and store path to nar hash mappings"
                jq --null-input "''${JQ_COMMON_FLAGS[@]}" \
                  --slurpfile packedHashToUnpackedSrc "$packedHashToUnpackedSrcOutPathJSONPath" \
                  --slurpfile unpackedSrcToNarHash "$unpackedSrcOutPathToNarHashJSONPath" \
                  '$packedHashToUnpackedSrc[0] | map_values($unpackedSrcToNarHash[0][.])' \
                  > "$out"
              ''
              # Cleanup
              + ''
                rm "$unpackedSrcOutPathToNarHashJSONPath"
              ''
            );
        aggregateUnpackedSrcOutPathToNarHashJSON = lib.importJSON aggregateUnpackedSrcOutPathToNarHash;

        # Do a lookup on each of the leaves of the original index (tarball hashes) to replace them with
        # the recursive NAR hash of the unpacked tarball.
        indexOfNarHashes = config.utils.mapIndexLeaves (
          { leaf, ... }: aggregateUnpackedSrcOutPathToNarHashJSON.${leaf}
        ) config.stages.stage0.result;
      in
      indexOfNarHashes;
  };
}
