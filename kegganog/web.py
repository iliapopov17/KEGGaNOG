import threading
import time
import webbrowser

import uvicorn


# The address the server will listen on.
# 127.0.0.1 means localhost only — the server is not exposed to the network,
# which is the correct behaviour for a local desktop tool.
HOST = "127.0.0.1"
PORT = 8000


def launch() -> None:
    """
    Start the KEGGaNOG web UI.

    Steps:
        1. Schedule the browser to open after a short delay (so the server
           has time to start before the browser tries to connect).
        2. Print a friendly message so the user knows what is happening.
        3. Start uvicorn — this call blocks until the user presses Ctrl+C.
    """

    _schedule_browser_open()

    print(f"\n  KEGGaNOG web UI is running at: http://{HOST}:{PORT}")
    print("  Press Ctrl+C to stop the server.\n")

    uvicorn.run(
        "kegganog.app:app",  # dotted path to the FastAPI app object in app.py
        host=HOST,
        port=PORT,
        log_level="warning",  # suppress uvicorn's verbose startup logs
        reload=False,  # no auto-reload needed for a local desktop tool
    )


def _schedule_browser_open() -> None:
    """
    Open the browser in a background thread after a short delay.

    Why a thread and a delay:
        uvicorn.run() is blocking — it never returns until Ctrl+C.
        If we called webbrowser.open() before uvicorn.run(), the server
        would not be ready yet and the browser would show a connection error.
        A daemon thread with a 1.5 s delay solves both problems:
        - The thread does not block the main thread from starting uvicorn.
        - The delay gives uvicorn enough time to bind the port and start
          accepting connections before the browser sends its first request.
        - daemon=True means the thread is killed automatically when the
          main process exits — no cleanup needed.
    """

    def _open() -> None:
        time.sleep(1.5)
        webbrowser.open(f"http://{HOST}:{PORT}")

    thread = threading.Thread(target=_open, daemon=True)
    thread.start()
