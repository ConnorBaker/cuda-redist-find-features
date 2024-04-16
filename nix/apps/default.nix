{
  perSystem =
    { pkgs, ... }:
    {
      apps = {
        generate-index.program =
          let
            generate-index = pkgs.callPackage ./generate-index { };
          in
          "${generate-index}/bin/${generate-index.meta.mainProgram}";
        generate-features.program =
          let
            generate-features = pkgs.callPackage ./generate-features { };
          in
          "${generate-features}/bin/${generate-features.meta.mainProgram}";
      };
    };
}
