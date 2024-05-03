{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
  inherit (lib.types) pathInStore;
in
{
  config.data.stages.stage3.description = "Create a map from unpacked tarball store path to NAR hash";
  options.data.stages.stage3 = mapAttrs (const mkOption) {
    result = {
      description = "Map from unpacked tarball store path to NAR hash";
      type = config.types.attrs pathInStore config.types.sriHash;
      # A default value would require both Import From Derivation and Recursive Nix.
    };
  };
}
