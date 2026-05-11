"""Shared pytest configuration for KEGGaNOG characterization tests."""

from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import pytest


# Headless, deterministic rendering for tests (matches web app Agg usage).
matplotlib.use("Agg")


@pytest.fixture(autouse=True)
def _silence_heatmap_side_effects(monkeypatch):
    """Avoid interactive windows and tqdm noise during heatmap tests."""
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    import tqdm as tqdm_mod

    class SilentTqdm(tqdm_mod.tqdm):
        def __init__(self, *args, **kwargs):
            kwargs["disable"] = True
            super().__init__(*args, **kwargs)

    monkeypatch.setattr(tqdm_mod, "tqdm", SilentTqdm)
