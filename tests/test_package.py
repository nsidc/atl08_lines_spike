from __future__ import annotations

import importlib.metadata

import alt08_lines as m


def test_version() -> None:
    assert importlib.metadata.version("alt08_lines") == m.__version__
