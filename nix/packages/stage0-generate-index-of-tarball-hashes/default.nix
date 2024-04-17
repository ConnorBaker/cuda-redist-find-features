{
  buildPackages,
  cuda-redist-lib,
  lib,
  python312,
  python312Packages,
  writers,
}:
let
  dirName = builtins.baseNameOf (builtins.toString ./.);
  fileName = lib.strings.replaceStrings [ "-generate-" ] [ "-" ] dirName + ".json";
  scriptDrv =
    writers.makePythonWriter python312 python312Packages buildPackages.python312Packages
      "/bin/${dirName}"
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

        from cuda_redist_lib import mk_index

        with open("${fileName}", "w", encoding="utf-8") as file:
            json.dump(
                mk_index().model_dump(by_alias=True, mode="json"),
                file,
                indent=2,
                sort_keys=True,
            )
      '';
in
scriptDrv.overrideAttrs { passthru.outputPath = fileName; }
