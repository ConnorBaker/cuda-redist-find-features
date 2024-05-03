{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
  inherit (lib.types) nonEmptyStr nullOr submodule;
in
{
  config.data.stages.stage0.description = "Parse NVIDIA's manifests and generate an index of hashes of tarballs.";
  options.data.stages.stage0 = mapAttrs (const mkOption) {
    result = {
      description = "Index of hashes of tarballs.";
      type = config.types.indexOf (submodule {
        options = mapAttrs (const mkOption) {
          relativePath = {
            type = nullOr nonEmptyStr;
            default = null;
          };
          sha256.type = config.types.sha256;
        };
      });
      # A default value would require impure derivations to run and access the internet.
    };
  };
}
