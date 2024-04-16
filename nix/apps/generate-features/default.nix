# NOTE:
# Make sure to run `nix run .#generate-index` prior to this script.
{
  lib,
  pkgs,
  jq,
  writeShellApplication,
}:
let
  indexModule = lib.modules.evalModules {
    specialArgs = {
      inherit pkgs;
    };
    modules = [
      ./module.nix
      { index = lib.trivial.importJSON ../generate-index/index.json; }
    ];
  };
in
writeShellApplication {
  name = "generate-fixed-output-derivations";
  # TODO: Pass sources through an environment variable to get a bash associative array?
  runtimeInputs = [ jq ];
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;
    blob = builtins.toJSON indexModule.config.index;
    passAsFile = [ "blob" ];
  };
  text = ''
    main() {
      local out="./nix/apps/generate-fixed-output-derivations/blob_home"
      mkdir -p "$out"
      echo "''${blobPath:?}" > "$out/index.json"
    }

    main
  '';
}
