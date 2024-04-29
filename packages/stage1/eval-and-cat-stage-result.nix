stageName:
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
      modules = [ ../../modules/stages/${stageName}.nix ];
    }).config
    )
    stages
    ;
  stage = stages.${stageName};
  # Remove all null values from the result.
  result = (lib.attrsets.filterAttrsRecursive (_: value: value != null)) stage.result;
in
writeShellApplication {
  inherit (stage) name;
  derivationArgs = {
    __contentAddressed = true;
    __structuredAttrs = true;
    strictDeps = true;

    preferLocalBuild = true;
    allowSubstitutes = false;
  };
  # Avoid using `cp` here because it'll error if the file already exists and have troubles with perms.
  text = ''
    cat < "${writers.writeJSON stage.outputPath result}" > "${stage.outputPath}"
  '';
}
