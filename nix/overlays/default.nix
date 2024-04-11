{
  flake.overlays.default = _final: prev: {
    pythonPackagesExtensions = prev.pythonPackagesExtensions ++ [
      (pythonFinal: _: {
        cuda-redist-find-features = pythonFinal.callPackage ../packages/cuda-redist-find-features.nix { };
      })
    ];
  };
}
