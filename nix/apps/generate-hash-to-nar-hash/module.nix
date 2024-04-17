{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.attrsets) mapAttrsToList;
  inherit (lib.lists) flatten;
  inherit (lib.options) mkOption;
  inherit (lib.strings) concatStringsSep removeSuffix;
  inherit (lib.types)
    addCheck
    enum
    functionTo
    nonEmptyListOf
    nonEmptyStr
    nullOr
    optionType
    raw
    strMatching
    submodule
    ;

  attrsOf' =
    keyType: elemType:
    addCheck (lib.types.attrsOf elemType) (
      value: builtins.all keyType.check (builtins.attrNames value)
    );
in
{
  options = {
    hashToUnpackedStorePath = mkOption {
      description = "A mapping from SRI hashes of (packed) tarballs to their unpacked store paths";
      type = attrsOf' config.types.sriHash nonEmptyStr;
      default = builtins.listToAttrs (
        config.utils.mapIndex (
          args@{ hash, redistName }:
          {
            name = hash;
            value =
              let
                url = config.utils.mkRedistURL redistName (config.utils.mkRelativePath args);
                tarballSrc = pkgs.fetchurl { inherit hash url; };
                # Thankfully, using srcOnly is equivalent to using fetchzip!
                unpackedSrc = pkgs.srcOnly {
                  name = removeSuffix ".tar.xz" tarballSrc.name;
                  src = tarballSrc;
                };
              in
              unpackedSrc.outPath;
          }
        ) config.index
      );
    };
    index = mkOption {
      description = "Redistributable name mapped to redistributable version mapped to a restructured manifest";
      type = config.types.index;
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
          "source" # Source-agnostic platform
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
      cudaVariant = mkOption {
        description = "The option type of a CUDA variant";
        type = optionType;
        default = strMatching "(None|cuda[0-9]+)";
      };
      index = mkOption {
        description = ''
          The option type of an index attribute set, mapping redistributable names to versioned manifests.
        '';
        type = optionType;
        default = attrsOf' config.types.redistName config.types.versionedManifests;
      };
      versionedManifests = mkOption {
        description = ''
          The option type of a versioned manifest attribute set, mapping version strings to manifests.
        '';
        type = optionType;
        default = attrsOf' config.types.version config.types.manifest;
      };
      manifest = mkOption {
        description = ''
          The option type of a manifest attribute set, mapping package names to release.
        '';
        type = optionType;
        default = attrsOf' config.types.packageName config.types.release;
      };
      releaseInfo = mkOption {
        description = "The option type of a releaseInfo attribute set.";
        type = optionType;
        default = submodule {
          options = {
            licensePath = mkOption {
              description = "The path to the license file in the redistributable tree";
              type = nullOr nonEmptyStr;
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
      packages = mkOption {
        description = "The option type of a package info attribute set, mapping platform to packageVariants.";
        type = optionType;
        default = attrsOf' config.types.platform config.types.packageVariants;
      };
      packageVariants = mkOption {
        description = "The option type of a package variant attribute set, mapping CUDA variant to SRI hash.";
        type = optionType;
        default = attrsOf' config.types.cudaVariant config.types.sriHash;
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
      version = mkOption {
        description = "The option type of a version with between two and four components";
        type = optionType;
        default = strMatching "([0-9]+)(\.[0-9]+){2,3}";
      };
      release = mkOption {
        description = "The option type of a release attribute set.";
        type = optionType;
        default = submodule {
          options = {
            releaseInfo = mkOption { type = config.types.releaseInfo; };
            packages = mkOption { type = config.types.packages; };
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
      mkRelativePath = mkOption {
        description = "Function to recreate a relative path for a redistributable";
        type = functionTo nonEmptyStr;
        default =
          {
            packageName,
            platform,
            releaseInfo,
            cudaVariant,
            ...
          }:
          concatStringsSep "/" [
            packageName
            platform
            (concatStringsSep "-" [
              packageName
              platform
              (releaseInfo.version + (if cudaVariant != "None" then "_${cudaVariant}" else ""))
              "archive.tar.xz"
            ])
          ];
      };

      mapIndex = mkOption {
        description = ''
          Function to map over the leaves of an index, returning a list of the results.

          The function must accept the following arguments:
          - redistName: The name of the redistributable
          - version: The version of the manifest
          - packageName: The name of the package
          - releaseInfo: The release information of the package
          - platform: The platform of the package
          - cudaVariant: The CUDA variant of the package
          - hash: The SRI hash of the package
        '';
        type = functionTo (functionTo raw);
        default =
          f: index:
          flatten (
            mapAttrsToList (
              redistName:
              mapAttrsToList (
                version:
                mapAttrsToList (
                  packageName:
                  { releaseInfo, packages }:
                  mapAttrsToList (
                    platform:
                    mapAttrsToList (
                      cudaVariant: hash:
                      f {
                        inherit
                          cudaVariant
                          hash
                          packageName
                          platform
                          redistName
                          releaseInfo
                          version
                          ;
                      }
                    )
                  ) packages
                )
              )
            ) index
          );
      };
    };
  };
}
