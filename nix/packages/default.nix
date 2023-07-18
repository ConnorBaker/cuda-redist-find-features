{
  perSystem = {pkgs, ...}: {
    packages = {
      cuda-redist-find-features = pkgs.python3Packages.callPackage ./cuda-redist-find-features.nix {};
    };
  };
}
