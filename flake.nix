{
  description = "Example development environment flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        packages = with pkgs; [
          ruff
          git-lfs
          python311
          zulu11
          maven
        ];
      in
      {
        devShell = pkgs.mkShell {
          buildInputs = packages;
          shellHook = ''
            echo "Welcome to the development shell!"
            if ! pip --version &>/dev/null; then
              python -m venv .venv
              .venv/bin/pip install -r requirements.txt
            fi
            source .venv/bin/activate
          '';
        };
      }
    );
}
