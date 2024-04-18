{ lib, ... }:
let
  inherit (lib.options) mkOption;
  inherit (lib.types) bool submodule;
in
{
  options = {
    outputs = mkOption {
      description = "Information about the outputs of the package";
      type = submodule {
        options = {
          bin = mkOption {
            description = ''
              A `bin` output requires that we have a non-empty `bin` directory containing at least one file with the
              executable bit set.
            '';
            type = bool;
          };
          dev = mkOption {
            description = ''
              A `dev` output requires that we have at least one of the following non-empty directories:

              - `include`
              - `lib/pkgconfig`
              - `share/pkgconfig`
              - `lib/cmake`
              - `share/aclocal`
            '';
            type = bool;
          };
          doc = mkOption {
            description = ''
              A `doc` output requires that we have at least one of the following non-empty directories:

              - `share/info`
              - `share/doc`
              - `share/gtk-doc`
              - `share/devhelp`
              - `share/man`
            '';
            type = bool;
          };
          lib = mkOption {
            description = ''
              A `lib` output requires that we have a non-empty lib directory containing at least one shared library.
            '';
            type = bool;
          };
          python = mkOption {
            description = ''
              A `python` output requires that we have a non-empty `python` directory.
            '';
            type = bool;
          };
          sample = mkOption {
            description = ''
              A `sample` output requires that we have a non-empty `samples` directory.
            '';
            type = bool;
          };
          static = mkOption {
            description = ''
              A `static` output requires that we have a non-empty lib directory containing at least one static library.
            '';
            type = bool;
          };
          stubs = mkOption {
            description = ''
              A `stubs` output requires that we have a non-empty `lib/stubs` or `stubs` directory containing at least one
              shared or static library.
            '';
            type = bool;
          };
        };
      };
    };
  };
}
