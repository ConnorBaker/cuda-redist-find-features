{ config, lib, ... }:
let
  inherit (lib.types)
    attrsOf
    enum
    functionTo
    nonEmptyListOf
    nonEmptyStr
    nullOr
    optionType
    strMatching
    submodule
    ;
  inherit (lib.strings) concatStringsSep;
  inherit (lib.options) mkOption;
in
{
  options = {
    index = mkOption {
      description = "Redistributable name mapped to redistributable version mapped to a restructured manifest";
      type = attrsOf (attrsOf config.types.manifest);
    };
    data = {
      platforms = mkOption {
        description = "List of platforms to use in creation of the platform type.";
        type = nonEmptyListOf nonEmptyStr;
        default = [
          "linux-aarch64"
          "linux-ppc64le"
          "linux-sbsa"
          "linux-x86_64"
        ];
      };
      redistUrlPrefix = mkOption {
        description = "The prefix of the URL for redistributable files";
        default = "https://developer.download.nvidia.com/compute";
        type = nonEmptyStr;
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
    };
    types = {
      manifestInfo = mkOption {
        description = "The option type of a manifest info attribute set";
        type = optionType;
        default = submodule {
          options = {
            date = mkOption { type = nullOr nonEmptyStr; };
            label = mkOption { type = nullOr nonEmptyStr; };
            product = mkOption { type = nullOr nonEmptyStr; };
            redist_name = mkOption { type = enum config.data.redistNames; };
          };
        };
      };
      releaseInfo = mkOption {
        description = "The option type of a release info attribute set";
        type = optionType;
        default = submodule {
          options = {
            license_path = mkOption { type = nullOr nonEmptyStr; };
            license = mkOption { type = nullOr nonEmptyStr; };
            name = mkOption { type = nullOr nonEmptyStr; };
            package_name = mkOption { type = nonEmptyStr; };
            version = mkOption { type = config.types.redistVersion; };
          };
        };
      };
      packageInfo = mkOption {
        description = "The option type of a package info attribute set";
        type = optionType;
        default = submodule {
          options = {
            cuda_variant = mkOption { type = nullOr nonEmptyStr; };
            platform = mkOption { type = enum config.types.platforms; };
            relative_path = mkOption { type = nonEmptyStr; };
            hash = mkOption { type = config.types.sriHash; };
          };
        };
      };
      platform = mkOption {
        description = "The option type of a platform";
        types = optionType;
        default = enum config.data.platforms;
      };
      redistName = mkOption {
        description = "The option type of allowable redistributables";
        type = optionType;
        default = enum config.data.redistNames;
      };
      redistUrl = mkOption {
        description = "The option type of a URL of for something in a redistributable's tree";
        type = optionType;
        default =
          let
            redistNamePattern = "(${concatStringsSep "|" config.data.redistNames})";
            redistUrlPrefixPattern = "(${config.data.redistUrlPrefix})";
            redistUrlPattern = "${redistUrlPrefixPattern}/${redistNamePattern}/redist/(.+)";
          in
          strMatching redistUrlPattern;
      };
      redistVersion = mkOption {
        description = "The option type of a version of a redistributable";
        type = optionType;
        # The default matches a version with between two and four components, each separated by a period.
        # TODO: Does Nix recognize curly braces or must I escape them?
        default = strMatching "([0-9]+)(\.[0-9]+){1,3}";
      };
      release = mkOption {
        description = "The option type of a restructured release attribute set";
        type = optionType;
        default = submodule {
          options = {
            release_info = mkOption { type = config.types.releaseInfo; };
            packages = mkOption { type = nonEmptyListOf config.types.packageInfo; };
          };
        };
      };
      manifest = mkOption {
        description = "The option type of a restructured manifest attribute set";
        type = optionType;
        default = submodule {
          options = {
            manifest_info = mkOption { type = config.types.manifestInfo; };
            releases = mkOption { type = nonEmptyListOf config.types.release; };
          };
        };
      };
      sriHash = mkOption {
        description = "The option type of a Subresource Integrity hash";
        type = optionType;
        default = strMatching "(md5|sha1|sha256|sha512)-([A-Za-z0-9+/]+={0,2})";
      };
    };
    utils = {
      mkRedistURL = mkOption {
        description = "Function to generate a URL for something in the redistributable tree";
        type = functionTo (functionTo config.types.redistUrl);
        default =
          redistName: relativePath: "${config.data.redistUrlPrefix}/${redistName}/redist/${relativePath}";
      };
    };
  };
}
