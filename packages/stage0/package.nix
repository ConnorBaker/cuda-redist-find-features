{
  buildPackages,
  cuda-redist-lib,
  lib,
  python312,
  python312Packages,
  writers,
}:
let
  inherit ((lib.modules.evalModules { modules = [ ../../modules/stages/stage0.nix ]; }).config.stages)
    stage0
    ;
in
writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
  "/bin/${stage0.name}"
  {
    flakeIgnore = [
      "E501" # line too long
      "W503" # line break before binary operator
    ];
    libraries = [
      cuda-redist-lib
      "pydantic"
    ];
  }
  ''
    import json

    from cuda_redist_lib.index import mk_index

    with open("${stage0.outputPath}", "w", encoding="utf-8") as file:
        json.dump(
            mk_index().model_dump(by_alias=True, mode="json"),
            file,
            indent=2,
            sort_keys=True,
        )
        file.write("\n")
  ''
