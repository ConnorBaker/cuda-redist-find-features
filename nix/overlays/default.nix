{
  flake.overlays.default = final: prev: {
    regen-readme = final.callPackage ../packages/regen-readme {};
    pythonPackagesExtensions =
      prev.pythonPackagesExtensions
      ++ [
        (pythonFinal: _: {
          cuda-redist-find-features = pythonFinal.callPackage ../packages/cuda-redist-find-features.nix {};
        })
      ];
  };
}
