{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs mapAttrsToList;
  inherit (lib.lists) flatten;
  inherit (lib.options) mkOption;
  inherit (lib.strings) concatStringsSep;
  inherit (lib.types) functionTo nonEmptyStr raw;
in
{
  options.utils = {
    mapIndexLeaves = mkOption {
      description = ''
        Function to map over the leaves of an index, replacing them with the result of the function.

        The function must accept the following arguments:
        - cudaVariant: The CUDA variant of the package
        - leaf: The leaf of the index
        - packageName: The name of the package
        - platform: The platform of the package
        - redistName: The name of the redistributable
        - releaseInfo: The release information of the package
        - version: The version of the manifest
      '';
      type = functionTo (functionTo raw);
      default =
        f: index:
        mapAttrs (
          redistName:
          mapAttrs (
            version:
            mapAttrs (
              packageName:
              { releaseInfo, packages }:
              {
                inherit releaseInfo;
                packages = mapAttrs (
                  platform:
                  mapAttrs (
                    cudaVariant: leaf:
                    f {
                      inherit
                        cudaVariant
                        leaf
                        packageName
                        platform
                        redistName
                        releaseInfo
                        version
                        ;
                    }
                  )
                ) packages;
              }
            )
          )
        ) index;
    };
    mapIndexLeavesToList = mkOption {
      description = ''
        Function to map over the leaves of an index, returning a list of the results.

        The function must accept the following arguments:
        - cudaVariant: The CUDA variant of the package
        - leaf: The leaf of the index
        - packageName: The name of the package
        - platform: The platform of the package
        - redistName: The name of the redistributable
        - releaseInfo: The release information of the package
        - version: The version of the manifest
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
                    cudaVariant: leaf:
                    f {
                      inherit
                        cudaVariant
                        leaf
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
  };
}