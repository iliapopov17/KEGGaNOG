"""Tests for kegganog.web (launch + _schedule_browser_open)."""

from __future__ import annotations

from unittest.mock import patch


def test_schedule_browser_open_opens_correct_url(monkeypatch):
    opened_urls: list[str] = []
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: opened_urls.append(url))

    from kegganog.web import _schedule_browser_open

    _schedule_browser_open()

    import time as _time

    _time.sleep(0.1)

    assert opened_urls == ["http://127.0.0.1:8000"]


def test_launch_prints_url_and_starts_server(monkeypatch, capsys):
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    with patch("uvicorn.run") as mock_run:
        from kegganog.web import launch

        launch()

    captured = capsys.readouterr()
    assert "http://127.0.0.1:8000" in captured.out
    mock_run.assert_called_once()


def test_launch_passes_correct_app_string(monkeypatch):
    monkeypatch.setattr("kegganog.web.time.sleep", lambda _: None)
    monkeypatch.setattr("webbrowser.open", lambda url: None)

    with patch("uvicorn.run") as mock_run:
        from kegganog.web import launch

        launch()

    call_args = mock_run.call_args
    assert call_args[0][0] == "kegganog.app:app"
    assert call_args[1]["host"] == "127.0.0.1"
    assert call_args[1]["port"] == 8000
