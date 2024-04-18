{ config, lib, ... }:
let
  inherit (lib.options) mkOption;
in
{
  imports = [ ./.. ];
  config.stages.stage0 = {
    description = "Parse NVIDIA's manifests and generate an index of hashes of tarballs.";
    name = "stage0-generate-index-of-tarball-hashes";
  };
  options.stages.stage0.result = mkOption {
    description = "Index of hashes of tarballs.";
    type = config.types.indexOf config.types.sriHash;
  };
}
