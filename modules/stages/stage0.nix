{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
  inherit (lib.types) nonEmptyStr nullOr submodule;
in
{
  imports = [ ./.. ];
  config.stages.stage0 = {
    description = "Parse NVIDIA's manifests and generate an index of hashes of tarballs.";
    name = "stage0-generate-index-of-tarball-hashes";
  };
  options.stages.stage0 = mapAttrs (const mkOption) {
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
