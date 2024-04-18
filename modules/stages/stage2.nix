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
  inherit (lib.types) submodule;
  inherit (pkgs)
    cuda-redist-feature-detector
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
    type = config.types.indexOf (
      config.types.attrs config.types.sriHash (submodule {
        imports = [
          # Each feature detector should have a corresponding module that outputs the features.
          cuda-redist-feature-detector.modules.outputs
        ];
      })
    );
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
              features =
                runCommand "generate-features"
                  {
                    __contentAddressed = true;
                    __structuredAttrs = true;
                    strictDeps = true;

                    preferLocalBuild = true;
                    allowSubstitutes = false;

                    nativeBuildInputs = [ cuda-redist-feature-detector ];
                  }
                  ''
                    echo "Finding features for ${unpackedSrc}"
                    cuda-redist-feature-detector --store-path "${unpackedSrc}" > "$out"
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

              nativeBuildInputs = [
                cuda-redist-feature-detector
                jq
              ];

              JQ_COMMON_FLAGS = [
                "--compact-output"
                "--sort-keys"
                "--raw-output"
              ];
            }
            (
              # Declare our variables here
              ''
                local narHashToFeatureOutPathJSONPath="${narHashToFeatureOutPathJSON}"
                local -A narHashToFeature
              ''
              # For each NAR hash, we need to read the contents of the associated store path to
              # get the feature object.
              + ''
                echo "Reading feature objects from store paths in $narHashToFeatureOutPathJSONPath"
                while IFS=$'\t' read -r narHash featureOutPath; do
                  narHashToFeature["$narHash"]="$(jq "''${JQ_COMMON_FLAGS[@]}" '.' "$featureOutPath")"
                done < <(jq "''${JQ_COMMON_FLAGS[@]}" 'to_entries[] | "\(.key)\t\(.value)"' "$narHashToFeatureOutPathJSONPath")
              ''
              # Convert the associative array to a JSON string and serialize it to out.
              + ''
                echo "Serializing aggregation of NAR hashes to feature objects"
                jq --null-input "''${JQ_COMMON_FLAGS[@]}" \
                  '[$ARGS.positional | _nwise(2) | {(.[0]): (.[1] | fromjson)}] | add' \
                  --args "''${narHashToFeature[@]@k}" \
                  > "$out"
              ''
            );
        aggregateNarHashToFeatureJSON = lib.importJSON aggregateNarHashToFeature;

        # Do a lookup on each of the leaves of the original index (NAR hashes) and map them to the feature object.
        indexOfNarHashToFeatures = config.utils.mapIndexLeaves (
          { leaf, ... }:
          let
            narHash = leaf;
          in
          {
            ${narHash} = aggregateNarHashToFeatureJSON.${narHash};
          }
        ) config.stages.stage1.result;
      in
      indexOfNarHashToFeatures;
  };
}
