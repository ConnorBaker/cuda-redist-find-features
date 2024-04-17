{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.attrsets) nameValuePair;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) pipe;
  inherit (lib.types) bool submodule;
  inherit (pkgs)
    fetchzip
    jq
    runCommand
    writers
    ;
in
{
  imports = [ ./stage1.nix ];
  config.stages = {
    # NOTE: We must use path-interpolation because string interpolation for paths is forbidden in pure evaluation mode.
    stage1.result = lib.trivial.importJSON ../../${config.stages.stage1.outputPath};
    stage2 = {
      description = "Replace the NAR hashes of the unpacked tarballs with a feature object";
      name = "stage2-generate-index-of-features";
    };
  };
  options.stages.stage2.result = mkOption {
    description = "Index of features";
    type = config.types.indexOf (submodule {
      options = {
        narHash = mkOption { type = config.types.sriHash; };
        features = mkOption { type = config.types.attrsOf bool; };
      };
    });
    default =
      let
        narHashToFeatureOutPathJSON = pipe config.stages.stage1.result [
          (config.utils.mapIndexLeavesToList (
            args@{ leaf, redistName, ... }:
            let
              hash = leaf;
              unpackedSrc = fetchzip {
                inherit hash;
                url = config.utils.mkRedistURL redistName (config.utils.mkRelativePath args);
              };
              # TODO: implement feature checks
              features =
                runCommand "generate-features"
                  {
                    __contentAddressed = true;
                    __structuredAttrs = true;
                    strictDeps = true;

                    preferLocalBuild = true;
                    allowSubstitutes = false;
                  }
                  ''
                    local src="${unpackedSrc}"
                    echo '{
                      "someFeature": true
                    }' > "$out"
                  '';
            in
            nameValuePair hash features.outPath
          ))
          builtins.listToAttrs
          (writers.writeJSON "nar-hash-to-feature-store-path.json")
        ];

        # Acccumulate and use all of the packages from the previous definition.
        # Forces a bottle-neck in Nix evaluation to ensure that the previous definition is evaluated.
        aggregateNarHashToFeature =
          runCommand "generate-aggregate-nar-hash-to-feature"
            {
              __contentAddressed = true;
              __structuredAttrs = true;
              strictDeps = true;

              preferLocalBuild = true;
              allowSubstitutes = false;

              nativeBuildInputs = [ jq ];
            }
            ''
              local narHashToFeatureOutPathJSONPath="${narHashToFeatureOutPathJSON}"

              # For each NAR hash, we need to read the contents of the associated store path to
              # get the feature object.

              local unpackedSrcToNarHashJSONPath="unpacked-src-to-nar-hash.json"

              # Get the NAR hashes for the store paths
              jq -r '.[]' < "$narHashToFeatureOutPathJSONPath" \
                | nix path-info --quiet --json --stdin \
                | jq -r 'with_entries(.value |= .narHash)' \
                > "$unpackedSrcToNarHashJSONPath"

              # Compose the hash to store path and store path to nar hash mappings
              # We do this partly because we cannot have strings which are store paths in the output!
              jq --null-input \
                --slurpfile packedHashToUnpackedSrc "$narHashToFeatureOutPathJSONPath" \
                --slurpfile unpackedSrcToNarHash "$unpackedSrcToNarHashJSONPath" \
                '$packedHashToUnpackedSrc[0] | map_values($unpackedSrcToNarHash[0][.])' \
                > "$out"

              # Cleanup
              rm "$unpackedSrcToNarHashJSONPath"
            '';
        aggregateNarHashToFeatureJSON = lib.importJSON aggregateNarHashToFeature;

        # Do a lookup on each of the leaves of the original index (NAR hashes) to replace them with
        # the feature object.
        indexOfNarHashes = config.utils.mapIndexLeaves (
          { leaf, ... }: aggregateNarHashToFeatureJSON.${leaf}
        ) config.stages.stage0.result;
      in
      indexOfNarHashes;
  };
}
