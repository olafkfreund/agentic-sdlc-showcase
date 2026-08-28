{
  # Everything the demo needs, pinned. A demo that depends on what happens to be
  # installed on the presenter's laptop is a demo that fails in front of the client —
  # and this repository's whole argument is that reproducibility is a control, not a
  # convenience.
  #
  #   nix develop            # the shell
  #   just demo              # the whole thing, narrated
  #
  # direnv users get it automatically: `direnv allow`.
  description = "Agentic SDLC showcase — runnable reference implementation of the playbook";

  inputs = {
    # A stable channel, deliberately. On nixos-unstable the fastapi build pulls a
    # test dependency whose own suite fails, which breaks the shell for a reason
    # that has nothing to do with this repository — exactly the class of surprise a
    # pinned demo environment exists to prevent.
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    ,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # The service and its gates. Kept in one list so the flake, devenv.nix and
        # pyproject.toml cannot drift into disagreeing about what the demo needs.
        python = pkgs.python312.withPackages (
          ps: with ps; [
            fastapi
            pydantic
            uvicorn
            pyyaml
            pytest
            httpx
            ruff
            build
          ]
        );

        tools = with pkgs; [
          python
          just
          gnumake
          git
          gh # Stages 2, 5 and 6 talk to GitHub through it
          jq
          curl
          coreutils
          bash
          ruby # jekyll, for previewing the site locally
          bundler
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          name = "agentic-sdlc";
          packages = tools;

          shellHook = ''
            export PY=python
            export PYTHONPATH="$PWD''${PYTHONPATH:+:$PYTHONPATH}"
            # The gates diff against a base ref; local runs have no CI to set it.
            export GATE_BASE_REF="''${GATE_BASE_REF:-origin/main}"

            echo
            echo "  agentic-sdlc  —  $(${pkgs.python312}/bin/python --version 2>&1)"
            echo
            echo "    just demo        the whole demo, narrated"
            echo "    just check       build, test, lint, gates"
            echo "    just negative    watch all twelve gates refuse"
            echo "    just swap        change agent vendor four ways, re-score each"
            echo "    just             every recipe"
            echo
          '';
        };

        # `nix flake check` builds this, so a broken shell is caught before a demo.
        packages.default = pkgs.writeShellApplication {
          name = "agentic-sdlc-check";
          runtimeInputs = tools;
          text = ''
            cd "''${1:-.}"
            export PY=python
            make build test lint gates
          '';
        };

        formatter = pkgs.nixfmt;
      }
    );
}
