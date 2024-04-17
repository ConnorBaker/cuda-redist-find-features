{
  perSystem =
    { config, pkgs, ... }:
    {
      devShells = {
        cuda-redist-feature-detector =
          let
            inherit (config.packages) cuda-redist-feature-detector;
            inherit (cuda-redist-feature-detector.optional-dependencies) dev;
          in
          pkgs.mkShell {
            strictDeps = true;
            inputsFrom = [ cuda-redist-feature-detector ];
            packages = dev;
          };
      };
    };
}
