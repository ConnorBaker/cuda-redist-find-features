{
  perSystem = {pkgs, ...}: {
    packages = {
      inherit (pkgs) regen-readme;
      inherit (pkgs.python311Packages) cuda-redist-find-features;
    };
  };
}
