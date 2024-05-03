{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
  inherit (lib.types) pathInStore;
in
{
  config.data.stages.stage2.description = "Create a map from unpacked tarball store path to feature";
  options.data.stages.stage2 = mapAttrs (const mkOption) {
    result = {
      description = "Map from unpacked tarball store path to feature";
      type = config.types.attrs pathInStore config.types.feature;
      # A default value would require Import From Derivation.
    };
  };
}
