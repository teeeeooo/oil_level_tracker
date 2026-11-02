"""The relay between the editor and its full-size video window (adapters/http/relay.py)."""

import threading
import time

from oil_tracker.adapters.http.relay import KEEP, Relay


def test_a_page_joins_at_the_current_number_and_gets_what_follows():
    relay = Relay()
    relay.post("a", "editor", {"n": 1})
    joined = relay.wait("a", -1, 5)
    assert joined["messages"] == [] and joined["seq"] == 1
    relay.post("b", "editor", {"n": 2})  # another channel
    relay.post("a", "window", {"n": 3})
    found = relay.wait("a", joined["seq"], 5)
    assert [(m["from"], m["message"]) for m in found["messages"]] == [("window", {"n": 3})]
    assert found["seq"] == 3 and not found["missed"]


def test_a_waiting_page_wakes_on_a_message_or_times_out():
    relay = Relay()
    began = time.monotonic()
    assert relay.wait("a", 0, 0.05) == {"seq": 0, "messages": [], "missed": False}
    assert time.monotonic() - began >= 0.04
    threading.Timer(0.05, relay.post, ("a", "editor", "hi")).start()
    found = relay.wait("a", 0, 5)
    assert [m["message"] for m in found["messages"]] == ["hi"]


def test_a_page_that_fell_behind_is_told():
    relay = Relay()
    for n in range(KEEP + 3):
        relay.post("a", "editor", n)
    found = relay.wait("a", 1, 0)
    assert found["missed"] and len(found["messages"]) == KEEP and found["messages"][0]["message"] == 3
    assert not relay.wait("a", found["seq"] - 1, 0)["missed"]
