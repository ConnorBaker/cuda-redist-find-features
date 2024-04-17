{
  perSystem =
    { config, pkgs, ... }:
    {
      packages = {
        # regen-readme = pkgs.callPackage ./regen-readme {
        #   inherit (config.packages) cuda-redist-find-features;
        # };
        cuda-redist-lib = pkgs.python312Packages.callPackage ./cuda-redist-lib { };
        cuda-redist-feature-detector = pkgs.python312Packages.callPackage ./cuda-redist-feature-detector {
          inherit (config.packages) cuda-redist-lib;
        };
        stage0 = pkgs.callPackage ./stage0-generate-index-of-tarball-hashes {
          inherit (config.packages) cuda-redist-lib;
        };
        stage1 = pkgs.callPackage ./stage1-generate-index-of-nar-hashes { };
        # stage2 = pkgs.callPackage ./stage2-generate-index-features { };
      };
    };
}
