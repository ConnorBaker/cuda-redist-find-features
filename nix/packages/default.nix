{
  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        regen-readme = pkgs.callPackage ./regen-readme {
          inherit (config.packages) cuda-redist-find-features;
        };
        inherit (pkgs.python312Packages) cuda-redist-find-features;
      };
    };
}
