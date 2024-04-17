{
  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        regen-readme = pkgs.callPackage ./regen-readme {
          inherit (config.packages) cuda-redist-find-features;
        };
        cuda-redist-lib = pkgs.python312Packages.callPackage ./cuda-redist-lib { };
        cuda-redist-find-features = pkgs.python312Packages.callPackage ./cuda-redist-find-features.nix { };
        stage0 = pkgs.callPackage ./stage0-generate-index-of-tarball-hashes {
          inherit (config.packages) cuda-redist-lib;
        };
        stage1 = pkgs.callPackage ./stage1-generate-index-of-nar-hashes {
          inherit (config.packages) stage0;
        };
      };
    };
}
