from __future__ import annotations

import importlib.metadata

import atl08_lines as m


def test_version() -> None:
    assert importlib.metadata.version("atl08_lines") == m.__version__
