{ lib, ... }:
let
  inherit (lib.attrsets) mapAttrs;
  inherit (lib.options) mkOption;
  inherit (lib.trivial) const;
  inherit (lib.types) attrsOf nonEmptyStr submodule;
in
{
  imports = [
    ./stage0.nix
    ./stage1.nix
    ./stage2.nix
    ./stage3.nix
    ./stage4.nix
  ];
  options.data = mapAttrs (const mkOption) {
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
                  default = config._module.args.name;
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
