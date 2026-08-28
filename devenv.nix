{ pkgs, ... }:

# devenv.sh entry point. `flake.nix` is the canonical definition — this exists so
# `devenv shell` works for people who use it, and it deliberately declares the same
# toolchain rather than a second, subtly different one.
#
#   devenv shell        then: just demo
#
# Or, without devenv:  nix develop

{
  name = "agentic-sdlc";

  packages = with pkgs; [
    just
    gnumake
    git
    gh # Stages 2, 5 and 6 talk to GitHub through it
    jq
    curl
    ruby # jekyll, for previewing the site locally
    bundler
  ];

  languages.python = {
    enable = true;
    package = pkgs.python312;
    venv = {
      enable = true;
      # One source of truth for the dependency set, the same file CI installs from.
      requirements = ''
        -e .[dev]
      '';
    };
  };

  env = {
    PY = "python";
    # The gates diff against a base ref; a local run has no CI to set one.
    GATE_BASE_REF = "origin/main";
  };

  enterShell = ''
    echo
    echo "  agentic-sdlc  —  devenv"
    echo
    echo "    just demo        the whole demo, narrated"
    echo "    just check       build, test, lint, gates"
    echo "    just negative    watch all twelve gates refuse"
    echo "    just swap        change agent vendor four ways, re-score each"
    echo "    just             every recipe"
    echo
  '';

  # `devenv test` runs the closed loop plus the control layer — the same four
  # commands AGENTS.md tells the agent to run, so the environment cannot drift
  # from what the pipeline checks.
  enterTest = ''
    make build test lint gates
  '';
}
