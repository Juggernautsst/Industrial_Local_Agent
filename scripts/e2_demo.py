#!/usr/bin/env python3
"""Interactive, model-free demonstration for the synthetic E2 boundary."""

from __future__ import annotations

import argparse
import dataclasses
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from industrial_local_agent.e2.demo import DemoRuntime
from industrial_local_agent.e2.errors import (
    AuditError,
    BundleVerificationError,
    IdentityError,
)


def print_header(title: str) -> None:
    print(f"\n=== {title} ===")


def print_bundle(response, label: str) -> None:
    bundle = response.bundle
    sources = [item.source_id for item in bundle.evidence]
    status = "[ALLOW]" if sources else "[NO EVIDENCE]"
    print(f"{status} {label}")
    print(f"        subject={bundle.subject_id} tenant={bundle.tenant_id} policy={bundle.policy_version}")
    print(f"        sources={sources or '[]'} content=omitted")
    print(f"        signed_bundle=yes audit_receipt={response.audit_receipt_event_id[:12]}...")


def demo_allowed(runtime: DemoRuntime) -> None:
    print_header("1. Authorized retrieval")
    response = runtime.retrieve("user-alice", "waveguide transmission", "alice-allowed")
    print_bundle(response, "Alice retrieves her tenant-a waveguide source")


def demo_isolation(runtime: DemoRuntime) -> None:
    print_header("2. Tenant isolation")
    carol = runtime.retrieve("user-carol", "control result", "carol-own")
    print_bundle(carol, "Carol retrieves tenant-b control source")
    alice = runtime.retrieve("user-alice", "control result", "alice-cross-tenant")
    print_bundle(alice, "Alice asks for the same query; tenant-b source is absent")


def demo_share_revoke(runtime: DemoRuntime) -> None:
    print_header("3. Share and revoke")
    before = runtime.retrieve("user-alice", "linewidth reviewer", "share-before")
    print_bundle(before, "Before Bob shares source-a2")
    runtime.policy.share_source("source-a2", "user-alice")
    shared = runtime.retrieve("user-alice", "linewidth reviewer", "share-after")
    print_bundle(shared, "After same-tenant explicit share")
    runtime.policy.revoke_share("source-a2", "user-alice")
    revoked = runtime.retrieve("user-alice", "linewidth reviewer", "share-revoked")
    print_bundle(revoked, "After share revocation")


def demo_forged_claim(runtime: DemoRuntime) -> None:
    print_header("4. Forged client claim")
    runtime.request_number += 1
    try:
        runtime.service.retrieve(
            runtime.token("user-alice"),
            request_id=f"demo-forged-{runtime.request_number}",
            query="control result",
            client_claims={"tenant_id": "tenant-b", "role": "admin"},
        )
    except IdentityError as error:
        print(f"[DENY] Client tenant/role claims rejected: {error}")
    else:
        print("[ERROR] Forged claim was unexpectedly accepted")


def demo_bundle_tamper(runtime: DemoRuntime) -> None:
    print_header("5. Bundle tamper detection")
    response = runtime.retrieve("user-alice", "waveguide", "bundle-tamper")
    request_id = response.bundle.request_id
    context = runtime.context_for("user-alice", request_id, response.bundle.delegation_id)
    tampered = dataclasses.replace(
        response.bundle,
        evidence=(dataclasses.replace(response.bundle.evidence[0], content="tampered"),),
    )
    try:
        runtime.service.verify_bundle_for_context(tampered, context)
    except BundleVerificationError as error:
        print(f"[DENY] Tampered evidence rejected: {error}")
    else:
        print("[ERROR] Tampered bundle was unexpectedly accepted")


def demo_audit(runtime: DemoRuntime) -> None:
    print_header("6. Content-free audit")
    try:
        runtime.audit.verify_chain()
    except AuditError as error:
        print(f"[ERROR] Audit chain verification failed: {error}")
        return
    fields = sorted(runtime.audit.events[-1]) if runtime.audit.events else []
    print(f"[PASS] audit hash chain verified; events={len(runtime.audit.events)}")
    print(f"       recorded_fields={fields}")
    print("       research_content=not recorded")


def run_all(runtime: DemoRuntime) -> None:
    demo_allowed(runtime)
    demo_isolation(runtime)
    demo_share_revoke(runtime)
    demo_forged_claim(runtime)
    demo_bundle_tamper(runtime)
    demo_audit(runtime)


def interactive(runtime: DemoRuntime) -> None:
    actions = {
        "1": demo_allowed,
        "2": demo_isolation,
        "3": demo_share_revoke,
        "4": demo_forged_claim,
        "5": demo_bundle_tamper,
        "6": demo_audit,
    }
    while True:
        print(
            "\nE2 demo menu (synthetic/offline/model-free)\n"
            "1) Authorized retrieval\n"
            "2) Tenant isolation\n"
            "3) Share and revoke\n"
            "4) Forged client claim\n"
            "5) Bundle tamper detection\n"
            "6) Audit verification\n"
            "7) Run all scenarios\n"
            "q) Quit"
        )
        choice = input("Select a scenario: ").strip().lower()
        if choice == "q":
            return
        if choice == "7":
            run_all(runtime)
        elif choice in actions:
            actions[choice](runtime)
        else:
            print("Unknown choice")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="run all scenarios and exit")
    args = parser.parse_args()
    print("Industrial Local Agent - Enterprise E2 demonstration")
    print("Synthetic data only; no LLM, cloud, UQ, Tidy3D, or blockchain calls.")
    runtime = DemoRuntime(ROOT / "fixtures/e2/synthetic_corpus.json")
    try:
        if args.all:
            run_all(runtime)
        else:
            interactive(runtime)
    finally:
        runtime.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
