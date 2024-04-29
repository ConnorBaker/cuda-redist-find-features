{ config, lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) nonEmptyStr nullOr submodule;
in
{
  imports = [ ./.. ];
  config.stages.stage0 = {
    description = "Parse NVIDIA's manifests and generate an index of hashes of tarballs.";
    name = "stage0-generate-index-of-tarball-hashes";
  };
  options.stages.stage0.result = mkOption {
    description = "Index of hashes of tarballs.";
    type = config.types.indexOf (submodule {
      options = {
        sha256 = mkOption { type = config.types.sha256; };
        relativePath = mkOption {
          description = "Relative path to the tarball or null if it can be reconstructed.";
          type = nullOr nonEmptyStr;
          default = null;
        };
      };
    });
    # A default value would require impure derivations to run and access the internet.
  };
}
