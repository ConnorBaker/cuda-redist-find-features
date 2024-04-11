{
  perSystem =
    { pkgs, ... }:
    {
      packages = {
        inherit (pkgs) regen-readme;
        inherit (pkgs.python312Packages) cuda-redist-find-features;
      };
    };
}
