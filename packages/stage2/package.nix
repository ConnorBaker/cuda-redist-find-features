{
  cuda-redist-feature-detector,
  jq,
  lib,
  pkgs,
  runCommand,
  writers,
  writeShellApplication,
}:
let
  inherit
    ((lib.modules.evalModules {
      specialArgs = {
        inherit pkgs;
      };
      modules = [ ../../modules ];
    }).config.data.stages
    )
    stage1
    stage2
    ;
  tarballHashToUnpackedTarballJSON = writers.writeJSON "${stage1.name}.json" stage1.result;
  # Having the result as a separate derivation rather than created during the execution of the main derivation
  # allows us to cache the result and avoid re-running the feature detection for the same tarball.
  result =
    runCommand "generate-map-from-unpacked-tarball-to-feature"
      {
        __contentAddressed = true;
        __structuredAttrs = true;
        strictDeps = true;

        preferLocalBuild = true;
        allowSubstitutes = false;

        nativeBuildInputs = [
          cuda-redist-feature-detector
          jq
        ];
        JQ_COMMON_FLAGS = [
          "--sort-keys"
          "--raw-output"
        ];
      }
      ''
        echo "Acquiring features for store paths in ${tarballHashToUnpackedTarballJSON}"
        jq "''${JQ_COMMON_FLAGS[@]}" '.[]' "${tarballHashToUnpackedTarballJSON}" \
          | cuda-redist-feature-detector --stdin \
          > "$out"
      '';
in
writeShellApplication {
  inherit (stage2) name;
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  # Avoid using `cp` here because it'll error if the file already exists and have troubles with perms.
  text = ''
    cat < "${result}" > "./modules/data/stages/${stage2.name}.json"
  '';
}
