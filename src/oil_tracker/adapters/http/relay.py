"""Messages between two pages of the app, through the server: the editor and its full-size video
window (Product SSOT §6) are two WebView windows that share no browser channel."""

from __future__ import annotations

import threading
from collections import deque
from typing import Any

KEEP = 64  # messages kept per channel; a page that fell further behind asks for the state again


class Relay:
    """Channels of numbered messages. A page posts to a channel and waits for the messages after the
    last number it has seen (long polling)."""

    def __init__(self) -> None:
        self._changed = threading.Condition()
        self._channels: dict[str, deque[dict[str, Any]]] = {}
        self._dropped: dict[str, int] = {}  # the newest number each channel let go
        self._seq = 0

    def post(self, channel: str, sender: str, message: Any) -> int:
        with self._changed:
            self._seq += 1
            kept = self._channels.setdefault(channel, deque())
            kept.append({"seq": self._seq, "from": sender, "message": message})
            while len(kept) > KEEP:
                self._dropped[channel] = kept.popleft()["seq"]
            self._changed.notify_all()
            return self._seq

    def wait(self, channel: str, after: int, timeout: float) -> dict[str, Any]:
        """The channel's messages numbered above after, waiting up to timeout seconds for one. A page
        joins with after < 0 and gets only the number to wait after. `missed` says some messages
        after `after` were let go before the page asked."""
        with self._changed:
            if after < 0:
                return {"seq": self._seq, "messages": [], "missed": False}

            def newer() -> list[dict[str, Any]]:
                return [m for m in self._channels.get(channel, ()) if m["seq"] > after]

            self._changed.wait_for(lambda: bool(newer()), timeout)
            found = newer()
            return {
                "seq": found[-1]["seq"] if found else after,
                "messages": found,
                "missed": self._dropped.get(channel, 0) > after,
            }
