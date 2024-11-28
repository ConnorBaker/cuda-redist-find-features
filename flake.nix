{
  description = "A flake for cuda-redist-find-features";
  inputs = {
    flake-parts = {
      inputs.nixpkgs-lib.follows = "nixpkgs";
      url = "github:hercules-ci/flake-parts";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pre-commit-hooks-nix = {
      inputs = {
        nixpkgs-stable.follows = "nixpkgs";
        nixpkgs.follows = "nixpkgs";
      };
      url = "github:cachix/git-hooks.nix";
    };
    treefmt-nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/treefmt-nix";
    };
  };

  outputs =
    inputs:
    inputs.flake-parts.lib.mkFlake { inherit inputs; } {
      systems = [
        "aarch64-darwin"
        "aarch64-linux"
        "x86_64-darwin"
        "x86_64-linux"
      ];
      imports = [
        inputs.treefmt-nix.flakeModule
        inputs.pre-commit-hooks-nix.flakeModule
        ./nix
      ];
      perSystem =
        { config, ... }:
        {
          pre-commit.settings.hooks = {
            # Formatter checks
            treefmt.enable = true;

            # Nix checks
            deadnix.enable = true;
            nil.enable = true;
            statix.enable = true;
          };

          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              # Markdown, YAML, JSON
              prettier = {
                enable = true;
                includes = [
                  "*.json"
                  "*.md"
                  "*.yaml"
                ];
                settings = {
                  embeddedLanguageFormatting = "auto";
                  printWidth = 120;
                  tabWidth = 2;
                };
              };

              # Nix
              nixfmt.enable = true;

              # Python
              ruff.enable = true;

              # Shell
              shellcheck.enable = true;
              shfmt.enable = true;
            };
          };

          packages.default = config.packages.cuda-redist-find-features;
          devShells.default = config.devShells.cuda-redist-find-features;
        };
    };
}
