{ lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) listOf strMatching;
in
{
  options = {
    # TODO: We have an additional constraint that we cannot verify from here:
    # A package with a non-empty `cudaVersionsInLib` feature MUST have a "None" cudaVariant,
    # because a non-empty `cudaVersionsInLib` indicates that the tarball provides multiple
    # versions of the library/package for different CUDA versions.
    cudaVersionsInLib = mkOption {
      description = "Subdirectories of the `lib` directory which are named after CUDA versions";
      type = listOf (strMatching "^[[:digit:]]+(\.[[:digit:]]+)?$");
      default = [ ];
    };
  };
}
