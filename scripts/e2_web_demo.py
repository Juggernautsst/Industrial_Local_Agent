#!/usr/bin/env python3
"""Start the loopback-only browser demonstration for synthetic E2."""

from __future__ import annotations

import argparse
import secrets
import sys
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from industrial_local_agent.e2.demo_web import E2DemoHTTPServer


def _port(value: str) -> int:
    port = int(value)
    if not 0 <= port <= 65535:
        raise argparse.ArgumentTypeError("port must be between 0 and 65535")
    return port


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=_port, default=8780)
    parser.add_argument("--open", action="store_true", help="open the demo URL in the default browser")
    args = parser.parse_args()
    token = secrets.token_urlsafe(32)
    server = E2DemoHTTPServer(
        ("127.0.0.1", args.port),
        ROOT / "fixtures/e2/synthetic_corpus.json",
        ROOT / "src/industrial_local_agent/e2/demo_static",
        token,
    )
    port = server.server_address[1]
    url = f"http://127.0.0.1:{port}/#token={token}"
    print(f"READY {url}", flush=True)
    print("Synthetic data only; no model, cloud, UQ, Tidy3D, or blockchain calls.", flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
