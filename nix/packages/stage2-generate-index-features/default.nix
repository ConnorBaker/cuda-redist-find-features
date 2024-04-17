# NOTE:
# Make sure to run `nix run .#stage1 && git add .` prior to this script.
{
  lib,
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
      modules = [ ../../modules/stage2.nix ];
    }).config.stages
    )
    stage2
    ;
  result = writers.writeJSON stage2.outputPath stage2.result;
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
    cat < "${result}" > "${stage2.outputPath}"
  '';
}
