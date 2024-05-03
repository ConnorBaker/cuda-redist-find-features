{ lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.strings) replaceStrings;
  inherit (lib.trivial) const;
  inherit (lib.types) attrsOf nonEmptyStr submodule;
in
{
  options = mapAttrs (const mkOption) {
    stages = {
      description = "A collection of stages to run in the pipeline";
      type = submodule {
        freeformType = attrsOf (
          submodule (
            { config, ... }:
            {
              options = mapAttrs (const mkOption) {
                description = {
                  description = "The description of the stage.";
                  type = nonEmptyStr;
                };
                name = {
                  description = "The name of the stage.";
                  type = nonEmptyStr;
                };
                outputPath = {
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
  };
}
