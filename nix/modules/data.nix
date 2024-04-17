{ lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) nonEmptyListOf nonEmptyStr;
in
{
  options.data = {
    platforms = mkOption {
      description = "List of platforms to use in creation of the platform type.";
      type = nonEmptyListOf nonEmptyStr;
      default = [
        "linux-aarch64"
        "linux-ppc64le"
        "linux-sbsa"
        "linux-x86_64"
        "source" # Source-agnostic platform
      ];
    };
    redistNames = mkOption {
      description = "List of redistributable names to use in creation of the redistName type.";
      type = nonEmptyListOf nonEmptyStr;
      default = [
        "cublasmp"
        "cuda"
        "cudnn"
        "cudss"
        "cuquantum"
        "cusolvermp"
        "cusparselt"
        "cutensor"
        # "nvidia-driver",  # NOTE: Some of the earlier manifests don't follow our scheme.
        "nvjpeg2000"
        "nvpl"
        "nvtiff"
      ];
    };
    redistUrlPrefix = mkOption {
      description = "The prefix of the URL for redistributable files";
      default = "https://developer.download.nvidia.com/compute";
      type = nonEmptyStr;
    };
  };
}
