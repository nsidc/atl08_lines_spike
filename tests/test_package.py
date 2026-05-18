from __future__ import annotations

import importlib.metadata

import icesat2gis as m


def test_version() -> None:
    assert importlib.metadata.version("icesat2gis") == m.__version__
