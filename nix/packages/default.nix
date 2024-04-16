{
  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        regen-readme = pkgs.callPackage ./regen-readme {
          inherit (config.packages) cuda-redist-find-features;
        };
        cuda-redist-find-features = pkgs.python312Packages.callPackage ./cuda-redist-find-features.nix { };
      };
    };
}
