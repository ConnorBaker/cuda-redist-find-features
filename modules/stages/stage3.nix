{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) pathInStore;
  inherit (pkgs) cuda-redist-feature-detector;
in
{
  imports = [ ./stage1.nix ];
  config.stages.stage3 = {
    description = "Create a map from unpacked tarball to NAR hash";
    name = "stage3-generate-map-from-unpacked-tarball-to-nar-hash";
  };
  options.stages.stage3.result = mkOption {
    description = "Map from unpacked tarball to NAR hash";
    type = config.types.attrs pathInStore cuda-redist-feature-detector.submodule;
    # Default would require both Import From Derivation and Recursive Nix.
  };
}
