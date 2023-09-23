{
  perSystem = {pkgs, ...}: {
    devShells = {
      cuda-redist-find-features = let
        inherit (pkgs.python3Packages) cuda-redist-find-features;
        inherit (cuda-redist-find-features.optional-dependencies) dev;
      in
        pkgs.mkShell {
          strictDeps = true;
          inputsFrom = [cuda-redist-find-features];
          packages = dev;
        };
    };
  };
}
