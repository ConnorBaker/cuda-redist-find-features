# NOTE:
# Make sure to run `nix run .#generate-index` prior to this script.
{
  stage0,
  lib,
  fetchurl,
  srcOnly,
  nixVersions,
  writers,
  runCommand,
  writeShellApplication,
}:
let
  # We must use path-interpolation otherwise this is forbidden in pure evaluation mode.
  indexOfTarballHashes = lib.trivial.importJSON ../../../${stage0.passthru.outputPath};
  indexModule = lib.modules.evalModules {
    modules = [
      ./modules
      (
        { config, lib, ... }:
        let
          inherit (lib.options) mkOption;
          inherit (lib.strings) removeSuffix;
          inherit (lib.types) package submodule;
        in
        {
          options = {
            # TODO: Try IFD again here to see if we can still build in parallel?
            # Have a `runCommand` which uses recursive nix to get the narHash of the built package.
            indexOfUnpackedTarballs = mkOption {
              description = "A mapping from SRI hashes of (packed) tarballs to their unpacked store paths";
              type = config.types.indexOf (submodule {
                options = {
                  hash = mkOption { type = config.types.sriHash; };
                  package = mkOption { type = package; };
                };
              });
              default = config.utils.mapIndexLeaves (
                args@{ leaf, redistName, ... }:
                let
                  hash = leaf;
                in
                {
                  inherit hash;
                  package =
                    let
                      url = config.utils.mkRedistURL redistName (config.utils.mkRelativePath args);
                      tarballSrc = fetchurl { inherit hash url; };
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
                    unpackedSrc;
                }
              ) config.indexOfTarballHashes;
            };
            indexOfNarHashes = mkOption {
              description = "Index of nar hashes of unpacked tarballs.";
              type = config.types.indexOf config.types.sriHash;
              default = config.utils.mapIndexLeaves (
                { leaf, ... }:
                let
                  inherit (leaf) package;
                  getNarHash =
                    (runCommand "get-nar-hash"
                      {
                        __contentAddressed = true;
                        __structuredAttrs = true;
                        strictDeps = true;
                        requiredSystemFeatures = [ "recursive-nix" ];

                        preferLocalBuild = true;
                        allowSubstitutes = false;

                        nativeBuildInputs = [ nixVersions.unstable ];
                        env.PACKAGE_STORE_PATH = package.outPath;
                      }
                      ''
                        main() {
                          local storePath="''${PACKAGE_STORE_PATH:?}"
                          echo "Getting nar hash for $storePath"

                          local oldstyleHash="$(nix-store --quiet --query --hash "$storePath")"
                          echo "Got old-style hash: $oldstyleHash"
                          local newstyleHash="$(nix-hash --quiet --to-sri "$oldstyleHash")"
                          echo "Got new-style hash: $newstyleHash"
                          echo "$newstyleHash" > "$out"
                        }

                        main
                      ''
                    ).overrideAttrs
                      (
                        finalAttrs: _prevAttrs: {
                          passthru.narHash = lib.strings.removeSuffix "\n" (builtins.readFile finalAttrs.finalPackage);
                        }
                      );
                in
                getNarHash.passthru.narHash
              ) config.indexOfUnpackedTarballs;
            };
            indexOfTarballHashes = mkOption {
              description = "Index of hashes of tarballs.";
              type = config.types.indexOf config.types.sriHash;
              default =
                let
                  smallIndex.cudnn."8.5.0".cudnn = indexOfTarballHashes.cudnn."8.5.0".cudnn;
                in
                # indexOfTarballHashes;
                smallIndex;
            };
          };
        }
      )
    ];
  };
  # hashToUnpackedStorePathJSON = lib.trivial.pipe indexModule.config.indexOfUnpackedTarballs [
  #   (indexModule.config.utils.mapIndexLeavesToList (
  #     { leaf, ... }: lib.attrsets.nameValuePair leaf.hash leaf.package.outPath
  #   ))
  #   builtins.listToAttrs
  #   (writers.writeJSON "hash-to-unpacked-store-path.json")
  # ];

  dirName = builtins.baseNameOf (builtins.toString ./.);
  fileName = lib.strings.removePrefix "stage0-generate-" dirName + ".json";
  indexOfNarHashesJSON = writers.writeJSON fileName indexModule.config.indexOfNarHashes;
in
# writers.writeJSON "hash-to-unpacked-store-path.json" indexModule.config.indexOfNarHashes
# writeShellApplication {
#   name = "generate-hash-to-nar-hash";
#   runtimeInputs = [
#     jq
#     nix
#   ];
#   excludeShellChecks = [ "SC2155" ];
#   derivationArgs = {
#     __structuredAttrs = true;
#     strictDeps = true;
#   };
#   text = ''
#     main() {
#       echo "Using hash-to-unpacked-store-path.json: ${hashToUnpackedStorePathJSON}"

#       # Get the nar hashes for the store paths
#       jq -r '.[]' < "${hashToUnpackedStorePathJSON}" \
#         | nix path-info --quiet --json --stdin \
#         | jq -r 'map({key: .path, value: .narHash}) | from_entries' \
#         > "unpacked-store-path-to-nar-hash.json"

#       # Compose the hash to store path and store path to nar hash mappings
#       jq --null-input \
#         --slurpfile paths "${hashToUnpackedStorePathJSON}" \
#         --slurpfile narHashes "unpacked-store-path-to-nar-hash.json" \
#         '$paths[0] | map_values($narHashes[0][.])' \
#         > "${fileName}"

#       rm -f "unpacked-store-path-to-nar-hash.json"
#     }

#     main
#   '';
# }

writeShellApplication {
  name = dirName;
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  # Avoid using `cp` here because it'll error if the file already exists and have troubles with perms.
  text = ''
    cat < "${indexOfNarHashesJSON}" > "${fileName}"
  '';
}
