{ lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.strings) replaceStrings;
  inherit (lib.types) attrsOf nonEmptyStr submodule;
in
{
  options.stages = mkOption {
    description = "A collection of stages to run in the pipeline";
    type = submodule {
      freeformType = attrsOf (
        submodule (
          { config, ... }:
          {
            options = {
              description = mkOption {
                description = "The description of the stage.";
                type = nonEmptyStr;
              };
              name = mkOption {
                description = "The name of the stage.";
                type = nonEmptyStr;
              };
              outputPath = mkOption {
                description = "The path to the result of the stage.";
                type = nonEmptyStr;
                default = replaceStrings [ "-generate-" ] [ "-" ] config.name + ".json";
              };
            };
          }
        )
      );
    };
    default = { };
  };
}
