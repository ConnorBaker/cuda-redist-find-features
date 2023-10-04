{
  inputs,
  self,
  ...
}: {
  imports = [
    ./devShells
    ./overlays
    ./packages
  ];
  perSystem = {system, ...}: {
    _module.args.pkgs = import inputs.nixpkgs {
      inherit system;
      config.allowUnfree = true;
      overlays = [self.overlays.default];
    };
  };
}
