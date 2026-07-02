"""Make the vendored, KLAP-v2-patched python-kasa shadow the stock 0.10.2.

Why: TP-Link firmware (new_klap:1, lv:2) changed the KLAP credential-hash
derivation. python-kasa 0.10.2 (pinned by HA core, baked into the image)
cannot authenticate those devices; the fix (python-kasa PR #1625, commit
dd92c05) is unmerged/unreleased. Pip-level overrides don't work because HA
considers the baked-in package "already satisfied", so we vendor the patched
library under _vendor/ and put it first on sys.path before anything imports
`kasa`. This module is imported at the very top of __init__.py, and Python
guarantees the package __init__ runs before any submodule, so every
`from kasa import ...` in this integration resolves to the vendored copy.

Delete this whole custom component once python-kasa ships the fix and HA
bumps its requirement.
"""

import sys
from pathlib import Path

_VENDOR = str(Path(__file__).parent / "_vendor")


def ensure() -> None:
    """Insert the vendored path and purge any stock kasa already imported."""
    if _VENDOR in sys.path:
        return
    for name in [m for m in sys.modules if m == "kasa" or m.startswith("kasa.")]:
        del sys.modules[name]
    sys.path.insert(0, _VENDOR)


ensure()
