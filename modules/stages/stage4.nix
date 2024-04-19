{
  config,
  lib,
  pkgs,
  ...
}:
let
  inherit (lib.options) mkOption;
  inherit (pkgs) cuda-redist-feature-detector;
in
{
  imports = [
    ./stage2.nix
    ./stage3.nix
  ];
  config.stages = {
    # NOTE: We must use path-interpolation because string interpolation for paths is forbidden in pure evaluation mode.
    # NOTE: We must use the materialized version of stage1 rather than the default value provided by the module system,
    # because the store paths are those of floating content-addressed store paths. We get the following error if we
    # don't use the materialized version:
    # error: the string '/033991s98wnd7zdm0crizrhsfjdanla7bj506phlxzlzl092xvq1' is not allowed to refer to a
    # store path (such as '!out!li5jji2jik59ck771ibpqiy2ps44ydrr-libcal-linux-sbsa-0.4.2.25_cuda11-archive-source.drv')
    stage1.result = lib.trivial.importJSON ../../${config.stages.stage1.outputPath};
    stage2.result = lib.trivial.importJSON ../../${config.stages.stage2.outputPath};
    stage3.result = lib.trivial.importJSON ../../${config.stages.stage3.outputPath};
    stage4 = {
      description = "Create an index of NAR hash to feature";
      name = "stage4-generate-index-of-nar-hash-to-feature";
    };
  };
  options.stages.stage4.result = mkOption {
    description = "Index of NAR hash to feature";
    type = config.types.indexOf (
      config.types.attrs config.types.sriHash cuda-redist-feature-detector.submodule
    );
    default =
      let
        indexOfTarballHashes = config.stages.stage0.result;
        tarballHashToUnpackedTarball = config.stages.stage1.result;
        unpackedTarballToFeature = config.stages.stage2.result;
        unpackedTarballToNarHash = config.stages.stage3.result;
      in
      config.utils.mapIndexLeaves (
        args:
        let
          tarballHash = args.leaf;
          unpackedTarball = tarballHashToUnpackedTarball.${tarballHash};
          feature = unpackedTarballToFeature.${unpackedTarball};
          narHash = unpackedTarballToNarHash.${unpackedTarball};
        in
        {
          ${narHash} = feature;
        }
      ) indexOfTarballHashes;
  };
}
