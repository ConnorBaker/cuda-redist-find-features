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
  config.stages.stage2 = {
    description = "Create a map from unpacked tarball to feature";
    name = "stage2-generate-map-from-unpacked-tarball-to-feature";
  };
  options.stages.stage2.result = mkOption {
    description = "Map from unpacked tarball to feature";
    type = config.types.attrs pathInStore cuda-redist-feature-detector.submodule;
    # A default value would require Import From Derivation.
  };
}
