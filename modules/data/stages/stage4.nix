{ config, lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
in
{
  config.data.stages = {
    # NOTE: We must use path-interpolation because string interpolation for paths is forbidden in pure evaluation mode.
    # NOTE: We must use the materialized version of stage1 rather than the default value provided by the module system,
    # because the store paths are those of floating content-addressed store paths. We get the following error if we
    # don't use the materialized version:
    # error: the string '/033991s98wnd7zdm0crizrhsfjdanla7bj506phlxzlzl092xvq1' is not allowed to refer to a
    # store path (such as '!out!li5jji2jik59ck771ibpqiy2ps44ydrr-libcal-linux-sbsa-0.4.2.25_cuda11-archive-source.drv')
    stage2.result = lib.trivial.importJSON ./stage2.json;
    stage3.result = lib.trivial.importJSON ./stage3.json;
    stage4.description = "Create an index of packageInfo";
  };
  options.data.stages.stage4 = mapAttrs (const mkOption) {
    result = {
      description = "Index of packageInfo";
      type = config.types.indexOf config.types.packageInfo;
      default =
        let
          indexOfTarballHashes = config.data.stages.stage0.result;
          tarballHashToUnpackedTarball = config.data.stages.stage1.result;
          unpackedTarballToFeature = config.data.stages.stage2.result;
          unpackedTarballToNarHash = config.data.stages.stage3.result;
        in
        config.utils.mapIndexLeaves (
          args:
          let
            tarballHash = args.leaf.sha256;
            unpackedTarball = tarballHashToUnpackedTarball.${tarballHash};
            feature = unpackedTarballToFeature.${unpackedTarball};
            narHash = unpackedTarballToNarHash.${unpackedTarball};
          in
          args.leaf // { inherit feature narHash; }
        ) indexOfTarballHashes;
    };
  };
}
