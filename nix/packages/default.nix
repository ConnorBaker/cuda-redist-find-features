{
  perSystem = {pkgs, ...}: {
    packages = {
      inherit (pkgs) regen-readme;
      inherit (pkgs.python3Packages) cuda-redist-find-features;
    };
  };
}
