"""Tests for kegganog.web — launch() and _open_browser_delayed()."""

from __future__ import annotations

from unittest.mock import patch

from kegganog.web import _open_browser_delayed


def test_open_browser_delayed_opens_correct_url(monkeypatch):
    opened: list[str] = []
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: opened.append(url))

    _open_browser_delayed("http://127.0.0.1:8000", 0)

    assert opened == ["http://127.0.0.1:8000"]


def test_launch_prints_url_to_stdout(monkeypatch, capsys):
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    with patch("uvicorn.run"):
        from kegganog.web import launch

        launch()

    assert "http://127.0.0.1:8000" in capsys.readouterr().out


def test_launch_calls_uvicorn_once(monkeypatch):
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    with patch("uvicorn.run") as mock_run:
        from kegganog.web import launch

        launch()

    mock_run.assert_called_once()


def test_launch_passes_correct_app_host_port(monkeypatch):
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    with patch("uvicorn.run") as mock_run:
        from kegganog.web import launch

        launch()

    args, kwargs = mock_run.call_args
    assert args[0] == "kegganog.app:app"
    assert kwargs["host"] == "127.0.0.1"
    assert kwargs["port"] == 8000
