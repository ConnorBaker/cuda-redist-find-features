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
      overlays = [self.overlays.default];
    };
  };
}
