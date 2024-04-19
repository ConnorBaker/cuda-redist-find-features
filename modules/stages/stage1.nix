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
  inherit (lib.types) path;
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
    # NOTE: We cannot use `pathInStore` as the value type because these are content-addressed derivations,
    # and so their store path is floating (i.e., not known until they are built).
    # Aside from nonEmptyStr, this is the most specific type we can get.
    # Do note that when this attribute set is serialized, the paths are in fact valid store paths.
    # NOTE: We cannot use `package` because in stage4, we are unable to get the outPath of the derivation
    # to index the data created in stage2 and stage3:
    # error: 'builtins.storePath' is not allowed in pure evaluation mode
    type = config.types.attrs config.types.sriHash path;
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
          nameValuePair hash unpackedSrc.outPath
        ))
        builtins.listToAttrs
      ];
  };
}
