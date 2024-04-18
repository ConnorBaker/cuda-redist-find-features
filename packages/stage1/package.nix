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
      modules = [ ../../modules/stages/stage1.nix ];
    }).config.stages
    )
    stage1
    ;
in
writeShellApplication {
  inherit (stage1) name;
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  # Avoid using `cp` here because it'll error if the file already exists and have troubles with perms.
  text = ''
    cat < "${writers.writeJSON stage1.outputPath stage1.result}" > "${stage1.outputPath}"
  '';
}
