{
  description = "A flake for cuda-redist-find-features";
  inputs = {
    flake-parts = {
      inputs.nixpkgs-lib.follows = "nixpkgs";
      url = "github:hercules-ci/flake-parts";
    };
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs";
    pre-commit-hooks-nix = {
      inputs = {
        flake-utils.follows = "flake-utils";
        nixpkgs-stable.follows = "nixpkgs";
        nixpkgs.follows = "nixpkgs";
      };
      url = "github:cachix/pre-commit-hooks.nix";
    };
  };

  outputs = inputs:
    inputs.flake-parts.lib.mkFlake {inherit inputs;} {
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-darwin"
        "x86_64-linux"
      ];
      imports = [
        inputs.pre-commit-hooks-nix.flakeModule
        ./nix
      ];
      perSystem = {
        config,
        pkgs,
        ...
      }: {
        formatter = pkgs.alejandra;
        pre-commit.settings = {
          hooks = {
            # Nix checks
            alejandra.enable = true;
            deadnix.enable = true;
            nil.enable = true;
            statix.enable = true;
            # Python checks
            black.enable = true;
            mypy.enable = true;
            pyright.enable = true;
            ruff.enable = true;
          };
          settings = let
            # We need to provide wrapped version of mypy and pyright which can find our imports.
            wrapper = name:
              pkgs.writeShellScript name ''
                source ${config.devShells.default}
                ${name} "$@"
              '';
          in {
            mypy.binPath = "${wrapper "mypy"}";
            pyright.binPath = "${wrapper "pyright"}";
          };
        };
        packages.default = config.packages.cuda-redist-find-features;
        devShells.default = config.devShells.cuda-redist-find-features;
      };
    };
}
