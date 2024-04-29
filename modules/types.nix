{ config, lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.strings) concatStringsSep;
  inherit (lib.types)
    addCheck
    enum
    functionTo
    nonEmptyStr
    nullOr
    optionType
    strMatching
    submodule
    ;
in
{
  options.types = {
    # TODO: Look into how `pkgs` makes an option type by overriding another option type:
    # https://github.com/NixOS/nixpkgs/blob/a6cc776496975eaef2de3218505c85bb5059fccb/lib/types.nix#L524-L530
    # We should do that for `attrs` and `function` to make docs more readable.
    # TODO: Not able to look at the keys in aggregate -- each typing decision is made per-key.
    attrs = mkOption {
      description = "The option type of an attribute set with typed keys and values.";
      type = functionTo (functionTo optionType);
      default =
        keyType: valueType:
        addCheck (lib.types.attrsOf valueType) (
          attrs: builtins.all keyType.check (builtins.attrNames attrs)
        );
    };
    cudaVariant = mkOption {
      description = "The option type of a CUDA variant";
      type = optionType;
      default = strMatching "^(None|cuda[[:digit:]]+)$";
    };
    indexOf = mkOption {
      description = ''
        The option type of an index attribute set, mapping redistributable names to versionedManifestsOf leafType.
      '';
      type = functionTo optionType;
      default =
        leafType: config.types.attrs config.types.redistName (config.types.versionedManifestsOf leafType);
    };
    # TODO: Look into how `pkgs` makes an option type by overriding another option type:
    # https://github.com/NixOS/nixpkgs/blob/a6cc776496975eaef2de3218505c85bb5059fccb/lib/types.nix#L524-L530
    # We should do that for `attrs` and `function` to make docs more readable.
    function = mkOption {
      description = "The option type of an function with typed argument and return values.";
      type = functionTo (functionTo optionType);
      default = argType: returnType: addCheck (lib.types.functionTo returnType) argType.check;
    };
    manifestsOf = mkOption {
      description = ''
        The option type of a manifest attribute set, mapping package names to releasesOf leafType.
      '';
      type = functionTo optionType;
      default = leafType: config.types.attrs config.types.packageName (config.types.releasesOf leafType);
    };
    packagesOf = mkOption {
      description = "The option type of a package info attribute set, mapping platform to packageVariantsOf leafType.";
      type = functionTo optionType;
      default =
        leafType: config.types.attrs config.types.platform (config.types.packageVariantsOf leafType);
    };
    packageVariantsOf = mkOption {
      description = "The option type of a package variant attribute set, mapping CUDA variant to leafType.";
      type = functionTo optionType;
      default = leafType: config.types.attrs config.types.cudaVariant leafType;
    };
    platform = mkOption {
      description = "The option type of a platform";
      type = optionType;
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
    releasesOf = mkOption {
      description = "The option type of a release attribute set of leafType.";
      type = functionTo optionType;
      default =
        leafType:
        submodule {
          options = {
            releaseInfo = mkOption { type = config.types.releaseInfo; };
            packages = mkOption { type = config.types.packagesOf leafType; };
          };
        };
    };
    releaseInfo = mkOption {
      description = "The option type of a releaseInfo attribute set.";
      type = optionType;
      default = submodule {
        options = {
          licensePath = mkOption {
            description = "The path to the license file in the redistributable tree";
            type = nullOr nonEmptyStr;
            default = null;
          };
          license = mkOption {
            description = "The license of the redistributable";
            type = nullOr nonEmptyStr;
          };
          name = mkOption {
            description = "The full name of the redistributable";
            type = nullOr nonEmptyStr;
          };
          version = mkOption {
            description = "The version of the redistributable";
            type = config.types.version;
          };
        };
      };
    };
    sha256 = mkOption {
      description = "The option type of a SHA-256, base64-encoded hash";
      type = optionType;
      default = strMatching "^[[:alnum:]+/]{64}$";
    };
    sriHash = mkOption {
      description = "The option type of a Subresource Integrity hash";
      type = optionType;
      # NOTE: This does not check the length of the hash!
      default = strMatching "^(md5|sha(1|256|512))-([[:alnum:]+/]+={0,2})$";
    };
    version = mkOption {
      description = "The option type of a version with at least one component";
      type = optionType;
      default = strMatching "^[[:digit:]]+(\.[[:digit:]]+)*$";
    };
    versionedManifestsOf = mkOption {
      description = ''
        The option type of a versioned manifest attribute set, mapping version strings to manifestsOf leafType.
      '';
      type = functionTo optionType;
      default = leafType: config.types.attrs config.types.version (config.types.manifestsOf leafType);
    };
  };
}
