{
  description = "A flake for cuda-redist-find-features";
  inputs = {
    flake-parts = {
      inputs.nixpkgs-lib.follows = "nixpkgs";
      url = "github:hercules-ci/flake-parts";
    };
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    pre-commit-hooks-nix = {
      inputs = {
        flake-utils.follows = "flake-utils";
        nixpkgs-stable.follows = "nixpkgs";
        nixpkgs.follows = "nixpkgs";
      };
      url = "github:cachix/pre-commit-hooks.nix";
    };
    treefmt-nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/treefmt-nix";
    };
  };

  nixConfig = {
    allow-import-from-derivation = true;
    extra-experimental-features = [
      "ca-derivations"
      "recursive-nix"
    ];
    keep-build-log = true;
    keep-derivations = true;
    keep-env-derivations = true;
    keep-failed = true;
    keep-going = true;
    keep-outputs = true;
    log-lines = 50;
    narinfo-cache-negative-ttl = 0;
    narinfo-cache-positive-ttl = 2592000; # 30 days
    pure-eval = true;
    show-trace = true;
    tarball-ttl = 2592000; # 30 days
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
        { config, pkgs, ... }:
        {
          legacyPackages = pkgs;
          pre-commit.settings.hooks = {
            # Formatter checks
            treefmt = {
              enable = true;
              package = config.treefmt.build.wrapper;
            };

            # Nix checks
            nil.enable = true;

            # Python checks
            pyright = {
              enable = true;
              settings.binPath =
                let
                  # We need to provide wrapped version of mypy and pyright which can find our imports.
                  # TODO: The script we're sourcing is an implementation detail of `mkShell` and we should
                  # not depend on it exisitng. In fact, the first few lines of the file state as much
                  # (that's why we need to strip them, sourcing only the content of the script).
                  wrapper =
                    name:
                    pkgs.writeShellScript name ''
                      source <(sed -n '/^declare/,$p' ${config.devShells.default})
                      ${name} "$@"
                    '';
                in
                builtins.toString (wrapper "pyright");
            };

            ruff.enable = true;
          };

          treefmt = {
            projectRootFile = "flake.nix";
            programs = {
              # JSON, Markdown, YAML
              prettier = {
                enable = true;
                includes = [
                  "*.json"
                  "*.md"
                  "*.yaml"
                ];
                excludes = [
                  "feature_manifests/*.json"
                  "redistrib_manifests/*.json"
                ];
                settings = {
                  embeddedLanguageFormatting = "auto";
                  printWidth = 120;
                  tabWidth = 2;
                };
              };

              # Nix
              deadnix.enable = true;
              nixfmt-rfc-style.enable = true;
              statix.enable = true;

              # Python
              ruff = {
                enable = true;
                format = true;
              };

              # Shell
              shellcheck.enable = true;
              shfmt.enable = true;

              # TOML
              taplo.enable = true;
            };
          };
          devShells.default = config.devShells.cuda-redist-feature-detector;
        };
    };
}
