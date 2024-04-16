{ inputs, ... }:
{
  imports = [
    ./apps
    ./devShells
    ./packages
  ];
  perSystem =
    { system, ... }:
    {
      _module.args.pkgs = import inputs.nixpkgs {
        inherit system;
        config.allowUnfree = true;
      };
    };
}
