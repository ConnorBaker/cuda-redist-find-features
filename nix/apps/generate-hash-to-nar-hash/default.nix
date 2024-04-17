# NOTE:
# Make sure to run `nix run .#generate-index` prior to this script.
{
  lib,
  pkgs,
  nix,
  jq,
  writers,
  writeShellApplication,
}:
let
  indexModule = lib.modules.evalModules {
    specialArgs = {
      inherit pkgs;
    };
    modules = [
      ./module.nix
      {
        index =
          let
            wholeIndex = lib.trivial.importJSON ../generate-index/index.json;
            smallIndex.cudnn."8.5.0".cudnn = wholeIndex.cudnn."8.5.0".cudnn;
          in
          smallIndex;
      }
    ];
  };
  hashToUnpackedStorePath = writers.writeJSON "hashToUnpackedStorePath.json" indexModule.config.hashToUnpackedStorePath;
in
writeShellApplication {
  name = "generate-hash-to-nar-hash";
  runtimeInputs = [
    jq
    nix
  ];
  excludeShellChecks = [ "SC2155" ];
  derivationArgs = {
    __structuredAttrs = true;
    strictDeps = true;
  };
  text = ''
    main() {
      local out="./nix/apps/generate-hash-to-nar-hash"
      mkdir -p "$out"

      cp -f "${hashToUnpackedStorePath}" "$out/hash-to-unpacked-store-path.json"

      # Get the nar hashes for the store paths
      jq -r '.[]' < "$out/hash-to-unpacked-store-path.json" \
        | nix path-info --quiet --json --stdin \
        | jq -r 'map({key: .path, value: .narHash}) | from_entries' \
        > "$out/unpacked-store-path-to-nar-hash.json"

      # Compose the hash to store path and store path to nar hash mappings
      jq --null-input \
        --slurpfile paths "$out/hash-to-unpacked-store-path.json" \
        --slurpfile narHashes "$out/unpacked-store-path-to-nar-hash.json" \
        '$paths[0] | map_values($narHashes[0][.])' \
        > "$out/hash-to-nar-hash.json"
      
      rm -f "$out/hash-to-unpacked-store-path.json" "$out/unpacked-store-path-to-nar-hash.json"
    }

    main
  '';
}
