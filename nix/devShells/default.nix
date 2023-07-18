{
  perSystem = {
    config,
    pkgs,
    ...
  }: {
    devShells = {
      cuda-redist-find-features = pkgs.mkShell {
        strictDeps = true;
        inputsFrom = [config.packages.cuda-redist-find-features];
        packages = config.packages.cuda-redist-find-features.optional-dependencies.dev;
      };
    };
  };
}
