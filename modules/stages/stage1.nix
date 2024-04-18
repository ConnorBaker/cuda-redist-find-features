{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.attrsets) nameValuePair;
  inherit (lib.options) mkOption;
  inherit (lib.strings) removeSuffix;
  inherit (lib.trivial) pipe;
  inherit (lib.types) package;
  inherit (pkgs) fetchurl srcOnly;
in
{
  imports = [ ./stage0.nix ];
  config.stages = {
    # NOTE: We must use path-interpolation because string interpolation for paths is forbidden in pure evaluation mode.
    # NOTE: We only define this here because we use it to create the result for stage1.
    stage0.result = lib.trivial.importJSON ../../${config.stages.stage0.outputPath};
    stage1 = {
      description = "Create a map from tarball hash to unpacked tarball.";
      name = "stage1-generate-map-from-tarball-hash-to-unpacked-tarball";
    };
  };
  options.stages.stage1.result = mkOption {
    description = "Map from tarball hash to unpacked tarball.";
    type = config.types.attrs config.types.sriHash package;
    default =
      let
        indexOfTarballHashes = config.stages.stage0.result;
      in
      pipe indexOfTarballHashes [
        (config.utils.mapIndexLeavesToList (
          args:
          let
            hash = args.leaf;
            tarballSrc = fetchurl {
              inherit hash;
              url = config.utils.mkRedistURL args.redistName (config.utils.mkRelativePath args);
            };
            # Thankfully, using srcOnly is equivalent to using fetchzip!
            unpackedSrc = srcOnly {
              __contentAddressed = true;
              __structuredAttrs = true;
              strictDeps = true;

              preferLocalBuild = true;
              allowSubstitutes = false;

              name = removeSuffix ".tar.xz" tarballSrc.name;
              src = tarballSrc;
            };
          in
          nameValuePair hash unpackedSrc
        ))
        builtins.listToAttrs
      ];
  };
}
