from __future__ import annotations

import http.client
import socket
import subprocess
import sys
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import Request, urlopen


def test_interactive_demo_all_scenarios_are_reproducible():
    root = Path(__file__).parents[2]
    result = subprocess.run(
        [sys.executable, str(root / "scripts/e2_demo.py"), "--all"],
        cwd=root,
        capture_output=True,
        text=True,
        check=True,
    )
    assert "[ALLOW] Alice retrieves her tenant-a waveguide source" in result.stdout
    assert "[NO EVIDENCE] Alice asks for the same query; tenant-b source is absent" in result.stdout
    assert "[DENY] Client tenant/role claims rejected" in result.stdout
    assert "[DENY] Tampered evidence rejected" in result.stdout
    assert "[PASS] audit hash chain verified" in result.stdout


def test_browser_demo_is_loopback_token_guarded_and_content_free():
    root = Path(__file__).parents[2]
    process = subprocess.Popen(
        [sys.executable, str(root / "scripts/e2_web_demo.py"), "--port", "0"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        ready_line = process.stdout.readline().strip()
        assert ready_line.startswith("READY http://127.0.0.1:")
        demo_url = ready_line.removeprefix("READY ")
        parsed = urlsplit(demo_url)
        token = parse_qs(parsed.fragment)["token"][0]
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        with urlopen(f"{base_url}/", timeout=5) as response:
            html = response.read().decode("utf-8")
            assert "Enterprise E2 Security Console" in html
            assert response.headers["X-Frame-Options"] == "DENY"

        connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
        try:
            connection.putrequest("GET", "/", skip_host=True)
            connection.putheader("Host", "[")
            connection.endheaders()
            response = connection.getresponse()
            assert response.status == 403
            response.read()
        finally:
            connection.close()

        connection = http.client.HTTPConnection(parsed.hostname, parsed.port, timeout=5)
        try:
            connection.putrequest("GET", "/api/state")
            connection.putheader("X-E2-Demo-Token", token)
            connection.putheader("X-E2-Demo-Token", token)
            connection.endheaders()
            response = connection.getresponse()
            assert response.status == 403
            response.read()
        finally:
            connection.close()

        try:
            urlopen(f"{base_url}/api/state", timeout=5)
        except HTTPError as error:
            assert error.code == 403
        else:
            raise AssertionError("State endpoint accepted a request without its startup token.")

        state_request = Request(
            f"{base_url}/api/state",
            headers={"X-E2-Demo-Token": token},
        )
        with urlopen(state_request, timeout=5) as response:
            snapshot = response.read().decode("utf-8")
            assert '"synthetic_only":true' in snapshot
            assert '"model_connected":false' in snapshot
            assert "Synthetic waveguide transmission" not in snapshot

        action_body = b'{"action":"retrieve","subject_id":"user-alice","query":"waveguide transmission"}'
        action_request = Request(
            f"{base_url}/api/action",
            data=action_body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "X-E2-Demo-Token": token,
            },
        )
        with urlopen(action_request, timeout=5) as response:
            result = response.read().decode("utf-8")
            assert '"kind":"allow"' in result
            assert '"source-a1"' in result
            assert '"research_content_in_response":false' in result
            assert "Synthetic waveguide transmission" not in result

        def raw_action_request(headers: bytes, body: bytes) -> int:
            with socket.create_connection((parsed.hostname, parsed.port), timeout=5) as connection:
                connection.sendall(
                    b"POST /api/action HTTP/1.1\r\n"
                    + f"Host: {parsed.hostname}:{parsed.port}\r\n".encode("ascii")
                    + f"X-E2-Demo-Token: {token}\r\n".encode("ascii")
                    + b"Content-Type: application/json\r\n"
                    + headers
                    + b"Connection: close\r\n\r\n"
                    + body
                )
                connection.shutdown(socket.SHUT_WR)
                response = http.client.HTTPResponse(connection)
                response.begin()
                response.read()
                return response.status

        assert raw_action_request(
            b"Content-Length: 25\r\nContent-Length: 25\r\n",
            b'{"action":"verify_audit"}',
        ) == 400
        assert raw_action_request(
            b"Content-Length: 100\r\n",
            b'{"action":"verify_audit"}',
        ) == 400
    finally:
        process.terminate()
        process.wait(timeout=5)
