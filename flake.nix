{
  description = "A flake for cuda-redist-find-features";
  inputs = {
    flake-parts = {
      inputs.nixpkgs-lib.follows = "nixpkgs";
      url = "github:hercules-ci/flake-parts";
    };
    git-hooks-nix = {
      inputs = {
        nixpkgs-stable.follows = "nixpkgs";
        nixpkgs.follows = "nixpkgs";
      };
      url = "github:cachix/git-hooks.nix";
    };
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix = {
      inputs.nixpkgs.follows = "nixpkgs";
      url = "github:numtide/treefmt-nix";
    };
  };

  nixConfig = {
    allow-import-from-derivation = false;
    keep-build-log = true;
    keep-derivations = true;
    keep-env-derivations = true;
    keep-failed = true;
    keep-going = true;
    keep-outputs = true;
    log-lines = 50;
    narinfo-cache-negative-ttl = 86400; # 1 day in seconds
    narinfo-cache-positive-ttl = 2592000; # 30 days in seconds
    pure-eval = true;
    show-trace = true;
    tarball-ttl = 2592000; # 30 days in seconds
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
        inputs.git-hooks-nix.flakeModule
      ];
      perSystem =
        {
          config,
          lib,
          pkgs,
          system,
          ...
        }:
        {
          _module.args.pkgs = import inputs.nixpkgs {
            inherit system;
            config.allowUnfree = true;
            overlays = [
              (
                final: _:
                lib.filesystem.packagesFromDirectoryRecursive {
                  inherit (final) callPackage;
                  directory = ./packages;
                }
              )
            ];
          };

          legacyPackages = pkgs;

          packages =
            let
              names = lib.trivial.pipe ./packages [
                builtins.readDir
                (lib.attrsets.filterAttrs (_: type: type == "directory"))
                builtins.attrNames
              ];
            in
            lib.attrsets.getAttrs names pkgs;

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
                excludes = [ "modules/data/indices/*.json" ];
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

          devShells = {
            cuda-redist-feature-detector =
              let
                inherit (pkgs) cuda-redist-feature-detector;
                inherit (cuda-redist-feature-detector.optional-dependencies) dev;
              in
              pkgs.mkShell {
                strictDeps = true;
                inputsFrom = [ cuda-redist-feature-detector ];
                packages = dev;
              };
            default = config.devShells.cuda-redist-feature-detector;
          };
        };
    };
}
