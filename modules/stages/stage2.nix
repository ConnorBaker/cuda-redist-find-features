{ config, lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) pathInStore;
in
{
  imports = [ ./stage1.nix ];
  config.stages.stage2 = {
    description = "Create a map from unpacked tarball store path to feature";
    name = "stage2-generate-map-from-unpacked-tarball-to-feature";
  };
  options.stages.stage2.result = mkOption {
    description = "Map from unpacked tarball store path to feature";
    type = config.types.attrs pathInStore config.types.feature;
    # A default value would require Import From Derivation.
  };
}
