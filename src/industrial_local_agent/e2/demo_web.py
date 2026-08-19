from __future__ import annotations

import dataclasses
import hmac
import ipaddress
import json
import math
import mimetypes
import socket
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .demo import DemoRuntime
from .errors import AuditError, BundleVerificationError, E2Error, IdentityError


MAX_REQUEST_BYTES = 16 * 1024
REQUEST_IDLE_TIMEOUT_SECONDS = 5
REQUEST_BODY_TIMEOUT_SECONDS = 4
REQUEST_DEADLINE_SECONDS = 6
RESPONSE_DEADLINE_MARGIN_SECONDS = 0.25

ACTION_FIELDS = {
    "retrieve": frozenset({"action", "subject_id", "query"}),
    "share": frozenset({"action"}),
    "revoke": frozenset({"action"}),
    "forged_claim": frozenset({"action"}),
    "tamper_bundle": frozenset({"action"}),
    "verify_audit": frozenset({"action"}),
    "reset": frozenset({"action"}),
}


class DuplicateJSONFieldError(ValueError):
    pass


def _reject_duplicate_json_fields(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONFieldError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def _bundle_result(response, title: str) -> dict[str, Any]:
    bundle = response.bundle
    source_ids = [item.source_id for item in bundle.evidence]
    return {
        "kind": "allow" if source_ids else "no_evidence",
        "title": title,
        "subject_id": bundle.subject_id,
        "tenant_id": bundle.tenant_id,
        "policy_version": bundle.policy_version,
        "source_ids": source_ids,
        "bundle_id": bundle.bundle_id,
        "bundle_signed": True,
        "audit_receipt_id": response.audit_receipt_event_id,
        "research_content_in_response": False,
    }


class DemoApplication:
    """Presentation adapter over the synthetic E2 runtime."""

    ALLOWED_SUBJECTS = {"user-alice", "user-bob", "user-carol"}

    def __init__(self, fixture_path: Path) -> None:
        self.fixture_path = fixture_path
        self.runtime = DemoRuntime(fixture_path)

    def _audit_events(self) -> list[dict[str, Any]]:
        events = []
        for body, receipt in zip(self.runtime.audit.events, self.runtime.audit.receipts):
            events.append(
                {
                    "sequence": receipt.sequence,
                    "event_type": body["event_type"],
                    "subject_id": body.get("subject_id"),
                    "tenant_id": body["tenant_id"],
                    "policy_version": body.get("policy_version"),
                    "source_ids": body.get("source_ids", []),
                    "outcome": body.get("outcome"),
                    "event_hash": receipt.event_hash,
                }
            )
        return events[-12:]

    def state(self) -> dict[str, Any]:
        state = self.runtime.public_state()
        state["audit_events"] = self._audit_events()
        return state

    def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action == "retrieve":
            subject_id = payload.get("subject_id")
            query = payload.get("query")
            if not isinstance(subject_id, str) or subject_id not in self.ALLOWED_SUBJECTS:
                raise ValueError("Unknown synthetic subject.")
            if not isinstance(query, str) or not query.strip() or len(query) > 500:
                raise ValueError("Query must contain 1 to 500 characters.")
            response = self.runtime.retrieve(subject_id, query.strip(), "web-retrieve")
            return _bundle_result(response, "Authorized retrieval completed")

        if action in {"share", "revoke"}:
            if action == "share":
                self.runtime.policy.share_source("source-a2", "user-alice")
                title = "source-a2 shared with Alice"
                kind = "allow"
            else:
                self.runtime.policy.revoke_share("source-a2", "user-alice")
                title = "Alice's source-a2 share revoked"
                kind = "deny"
            return {
                "kind": kind,
                "title": title,
                "policy_version": self.runtime.policy.version,
                "source_id": "source-a2",
                "subject_id": "user-alice",
            }

        if action == "forged_claim":
            self.runtime.request_number += 1
            try:
                self.runtime.service.retrieve(
                    self.runtime.token("user-alice"),
                    request_id=f"demo-web-forged-{self.runtime.request_number}",
                    query="control result",
                    client_claims={"tenant_id": "tenant-b", "role": "admin"},
                )
            except IdentityError as error:
                return {"kind": "deny", "title": "Forged client claims rejected", "reason": str(error)}
            raise RuntimeError("Forged claim was unexpectedly accepted.")

        if action == "tamper_bundle":
            response = self.runtime.retrieve("user-alice", "waveguide", "web-tamper")
            bundle = response.bundle
            context = self.runtime.context_for("user-alice", bundle.request_id, bundle.delegation_id)
            tampered = dataclasses.replace(
                bundle,
                evidence=(dataclasses.replace(bundle.evidence[0], content="tampered"),),
            )
            try:
                self.runtime.service.verify_bundle_for_context(tampered, context)
            except BundleVerificationError as error:
                return {
                    "kind": "deny",
                    "title": "Tampered bundle rejected",
                    "reason": str(error),
                    "bundle_id": bundle.bundle_id,
                }
            raise RuntimeError("Tampered bundle was unexpectedly accepted.")

        if action == "verify_audit":
            try:
                self.runtime.audit.verify_chain()
            except AuditError as error:
                return {"kind": "error", "title": "Audit chain verification failed", "reason": str(error)}
            return {
                "kind": "pass",
                "title": "Audit hash chain verified",
                "event_count": len(self.runtime.audit.events),
                "research_content_recorded": False,
            }

        if action == "reset":
            self.runtime.close()
            self.runtime = DemoRuntime(self.fixture_path)
            return {"kind": "pass", "title": "Synthetic demo state reset", "policy_version": 1}

        raise ValueError("Unknown demo action.")

    def close(self) -> None:
        self.runtime.close()


class E2DemoHTTPServer(HTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        fixture_path: Path,
        asset_directory: Path,
        session_token: str,
        *,
        request_deadline_seconds: float = REQUEST_DEADLINE_SECONDS,
    ) -> None:
        if not math.isfinite(request_deadline_seconds) or request_deadline_seconds <= 0:
            raise ValueError("request_deadline_seconds must be finite and positive")
        resolved_asset_directory = asset_directory.resolve()
        application = DemoApplication(fixture_path)
        try:
            super().__init__(server_address, E2DemoRequestHandler)
        except Exception:
            application.close()
            raise
        self.application = application
        self.asset_directory = resolved_asset_directory
        self.session_token = session_token
        self.request_deadline_seconds = request_deadline_seconds

    def server_close(self) -> None:
        try:
            self.application.close()
        finally:
            super().server_close()


class E2DemoRequestHandler(BaseHTTPRequestHandler):
    server: E2DemoHTTPServer

    def setup(self) -> None:
        super().setup()
        self._request_started_at = time.monotonic()
        self._request_deadline_expired = threading.Event()
        self.connection.settimeout(REQUEST_IDLE_TIMEOUT_SECONDS)
        self._deadline_timer = threading.Timer(
            self.server.request_deadline_seconds,
            self._expire_request,
        )
        self._deadline_timer.daemon = True
        self._deadline_timer.start()

    def handle(self) -> None:
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError):
            if not self._request_deadline_expired.is_set():
                raise

    def finish(self) -> None:
        try:
            try:
                super().finish()
            except (BrokenPipeError, ConnectionResetError):
                if not self._request_deadline_expired.is_set():
                    raise
        finally:
            self._deadline_timer.cancel()

    def _expire_request(self) -> None:
        self._request_deadline_expired.set()
        self.close_connection = True
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

    def log_message(self, format: str, *args: object) -> None:
        print(f"E2 demo: {format % args}")

    def _request_is_local(self) -> bool:
        try:
            return ipaddress.ip_address(self.client_address[0]).is_loopback
        except ValueError:
            return False

    def _host_is_local(self) -> bool:
        host_headers = self.headers.get_all("Host", failobj=[]) or []
        if len(host_headers) != 1:
            return False
        try:
            parsed = urlsplit(f"//{host_headers[0]}")
            port = parsed.port
        except ValueError:
            return False
        return (
            parsed.hostname in {"127.0.0.1", "localhost", "::1"}
            and parsed.username is None
            and parsed.password is None
            and not parsed.path
            and not parsed.query
            and not parsed.fragment
            and port in {None, self.server.server_address[1]}
        )

    def _authorized(self) -> bool:
        token_headers = self.headers.get_all("X-E2-Demo-Token", failobj=[]) or []
        if len(token_headers) != 1:
            return False
        supplied = token_headers[0]
        return bool(supplied) and supplied.isascii() and hmac.compare_digest(
            supplied,
            self.server.session_token,
        )

    def _read_request_body(self, length: int) -> bytes:
        response_margin = min(
            RESPONSE_DEADLINE_MARGIN_SECONDS,
            self.server.request_deadline_seconds / 2,
        )
        body_deadline = min(
            self._request_started_at + self.server.request_deadline_seconds - response_margin,
            time.monotonic() + REQUEST_BODY_TIMEOUT_SECONDS,
        )
        chunks = []
        remaining = length
        try:
            while remaining:
                timeout = body_deadline - time.monotonic()
                if timeout <= 0:
                    raise TimeoutError
                self.connection.settimeout(timeout)
                chunk = self.rfile.read1(min(remaining, 8 * 1024))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
        finally:
            self.connection.settimeout(REQUEST_IDLE_TIMEOUT_SECONDS)
        return b"".join(chunks)

    def _request_path(self) -> str | None:
        try:
            parsed = urlsplit(self.path)
        except ValueError:
            return None
        if (
            parsed.scheme
            or parsed.netloc
            or parsed.query
            or parsed.fragment
            or not parsed.path.startswith("/")
        ):
            return None
        return parsed.path

    def _send_headers(self, status: int, content_type: str, length: int) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(length))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header(
            "Content-Security-Policy",
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
            "connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'",
        )
        self.end_headers()

    def _json(self, value: dict[str, Any], status: int = HTTPStatus.OK) -> None:
        body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        self._send_headers(status, "application/json; charset=utf-8", len(body))
        self.wfile.write(body)

    def _fail(self, status: int, message: str) -> None:
        self._json({"error": message}, status)

    def _preflight(self, require_token: bool) -> bool:
        if not self._request_is_local() or not self._host_is_local():
            self._fail(HTTPStatus.FORBIDDEN, "The E2 demo accepts loopback requests only.")
            return False
        if require_token and not self._authorized():
            self._fail(HTTPStatus.FORBIDDEN, "A valid E2 demo startup token is required.")
            return False
        return True

    def do_GET(self) -> None:
        if not self._preflight(require_token=False):
            return
        path = self._request_path()
        if path is None:
            self._fail(HTTPStatus.BAD_REQUEST, "Request target is invalid.")
            return
        if path == "/api/state":
            if not self._authorized():
                self._fail(HTTPStatus.FORBIDDEN, "A valid E2 demo startup token is required.")
                return
            self._json(self.server.application.state())
            return
        asset_name = "index.html" if path == "/" else path.removeprefix("/")
        if asset_name not in {"index.html", "app.css", "app.js"}:
            self._fail(HTTPStatus.NOT_FOUND, "Not found.")
            return
        asset_path = (self.server.asset_directory / asset_name).resolve()
        if asset_path.parent != self.server.asset_directory or not asset_path.is_file():
            self._fail(HTTPStatus.NOT_FOUND, "Not found.")
            return
        body = asset_path.read_bytes()
        content_type = mimetypes.guess_type(asset_path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type == "application/javascript":
            content_type += "; charset=utf-8"
        self._send_headers(HTTPStatus.OK, content_type, len(body))
        self.wfile.write(body)

    def do_POST(self) -> None:
        if not self._preflight(require_token=True):
            return
        path = self._request_path()
        if path is None:
            self._fail(HTTPStatus.BAD_REQUEST, "Request target is invalid.")
            return
        if path != "/api/action":
            self._fail(HTTPStatus.NOT_FOUND, "Not found.")
            return
        if self.headers.get_content_type() != "application/json":
            self._fail(HTTPStatus.UNSUPPORTED_MEDIA_TYPE, "Actions require application/json.")
            return
        if self.headers.get("Transfer-Encoding"):
            self._fail(HTTPStatus.BAD_REQUEST, "Transfer-Encoding is not accepted.")
            return
        length_headers = self.headers.get_all("Content-Length", failobj=[]) or []
        if len(length_headers) != 1:
            self._fail(HTTPStatus.BAD_REQUEST, "Exactly one Content-Length header is required.")
            return
        length_text = length_headers[0]
        if not length_text.isascii() or not length_text.isdecimal():
            self._fail(HTTPStatus.BAD_REQUEST, "Content-Length is invalid.")
            return
        length = int(length_text)
        if not 1 <= length <= MAX_REQUEST_BYTES:
            self._fail(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, "Action payload is outside the size limit.")
            return
        try:
            body = self._read_request_body(length)
        except TimeoutError:
            self._fail(HTTPStatus.REQUEST_TIMEOUT, "Action payload timed out.")
            return
        if len(body) != length:
            self._fail(HTTPStatus.BAD_REQUEST, "Action payload is incomplete.")
            return
        try:
            payload = json.loads(body, object_pairs_hook=_reject_duplicate_json_fields)
        except DuplicateJSONFieldError:
            self._fail(HTTPStatus.BAD_REQUEST, "Action payload contains duplicate JSON fields.")
            return
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._fail(HTTPStatus.BAD_REQUEST, "Action payload is not valid JSON.")
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("action"), str):
            self._fail(HTTPStatus.BAD_REQUEST, "Action payload must be an object with an action.")
            return
        allowed_fields = ACTION_FIELDS.get(payload["action"])
        if allowed_fields is None:
            self._fail(HTTPStatus.BAD_REQUEST, "Unknown demo action.")
            return
        if set(payload) != allowed_fields:
            self._fail(HTTPStatus.BAD_REQUEST, "Action payload fields do not match the selected action.")
            return
        try:
            result = self.server.application.execute(payload["action"], payload)
        except (E2Error, ValueError) as error:
            self._fail(HTTPStatus.BAD_REQUEST, str(error))
            return
        except Exception:
            self._fail(HTTPStatus.INTERNAL_SERVER_ERROR, "The synthetic E2 action failed.")
            return
        self._json({"result": result, "state": self.server.application.state()})
