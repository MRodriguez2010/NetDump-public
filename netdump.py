"""Summarize browser network timing from a local HAR export or a loopback Chrome tab."""
import argparse
from collections import Counter
import json
from pathlib import Path
import time
from urllib.parse import urlsplit
from urllib.request import urlopen


def summarize(entries):
    counts = Counter()
    for method, status, mime in entries:
        method = str(method).upper()
        method = method if method in {"GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"} else "OTHER"
        status = int(status)
        family = str(mime).split("/", 1)[0].lower()
        family = family if family in {"application", "text", "image", "audio", "video", "font"} else "other"
        counts[method, status, family] += 1
    return [{"method": m, "status": s, "media_family": t, "count": count}
            for (m, s, t), count in sorted(counts.items())]


def from_har(path):
    entries = json.loads(path.read_text())["log"]["entries"]
    return summarize((e["request"]["method"], e["response"]["status"], e["response"]["content"].get("mimeType", "")) for e in entries)


def capture(port, target, seconds):
    import websocket
    with urlopen(f"http://127.0.0.1:{port}/json/list", timeout=5) as response:
        tabs = json.load(response)
    tab = next(t for t in tabs if t.get("id") == target and t.get("type") == "page")
    address = urlsplit(tab["webSocketDebuggerUrl"])
    if address.hostname not in {"localhost", "127.0.0.1", "::1"} or address.scheme != "ws":
        raise ValueError("Expected a loopback browser debugger.")
    sock = websocket.create_connection(address.geturl(), timeout=1, suppress_origin=True)
    methods, responses = {}, []
    try:
        sock.send(json.dumps({"id": 1, "method": "Network.enable"}))
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            try:
                event = json.loads(sock.recv())
            except websocket.WebSocketTimeoutException:
                continue
            data = event.get("params", {})
            if event.get("method") == "Network.requestWillBeSent":
                methods[data["requestId"]] = data["request"]["method"]
            if event.get("method") == "Network.responseReceived":
                r = data["response"]
                responses.append((methods.pop(data["requestId"], "OTHER"), r["status"], r.get("mimeType", "")))
    finally:
        sock.close()
    return summarize(responses)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--har", type=Path)
    source.add_argument("--tab", help="ID of the explicitly selected local debugging tab")
    parser.add_argument("--port", type=int, default=9222)
    parser.add_argument("--seconds", type=int, choices=range(1, 61), default=10, metavar="1–60")
    args = parser.parse_args()
    print(json.dumps(from_har(args.har) if args.har else capture(args.port, args.tab, args.seconds), indent=2))
