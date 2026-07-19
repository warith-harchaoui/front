"""
front_cli.__main__
==================

Enables ``python -m front_cli`` — a thin entry point that delegates to the Click
group in :mod:`front_cli.cli`. No logic lives here; it exists so the package is
runnable as a module as well as via the installed ``front`` console script.

Author
------
Project maintainers.
"""

from front_cli.cli import cli

if __name__ == "__main__":
    cli()
