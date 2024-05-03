{
  buildPackages,
  cuda-redist-lib,
  lib,
  python312,
  python312Packages,
  writers,
}:
let
  inherit ((lib.modules.evalModules { modules = [ ../../modules ]; }).config.data.stages) stage0;
in
writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
  "/bin/${stage0.name}"
  {
    flakeIgnore = [
      "E501" # line too long
      "W503" # line break before binary operator
    ];
    libraries = [ cuda-redist-lib ];
  }
  (builtins.readFile ./stage0.py)
