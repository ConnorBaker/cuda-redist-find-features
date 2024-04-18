{
  jq,
  lib,
  nixVersions,
  pkgs,
  writers,
  writeShellApplication,
}:
let
  inherit
    ((lib.modules.evalModules {
      specialArgs = {
        inherit pkgs;
      };
      modules = [ ../../modules/stages/stage3.nix ];
    }).config.stages
    )
    stage1
    stage3
    ;
  tarballHashToUnpackedTarballJSON = writers.writeJSON stage1.outputPath stage1.result;
in
writeShellApplication {
  inherit (stage3) name;
  runtimeInputs = [
    jq
    nixVersions.unstable
  ];
  runtimeEnv.JQ_COMMON_FLAGS = [
    "--sort-keys"
    "--raw-output"
  ];
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  text = ''
    echo "Acquiring NAR hashes for store paths in ${tarballHashToUnpackedTarballJSON}"
    jq "''${JQ_COMMON_FLAGS[@]}" '.[]' "${tarballHashToUnpackedTarballJSON}" \
      | nix path-info --quiet --json --stdin \
      | jq "''${JQ_COMMON_FLAGS[@]}" 'with_entries(.value |= .narHash)' \
      > "${stage3.outputPath}"
  '';
}
