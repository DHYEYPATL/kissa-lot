from __future__ import annotations

import argparse
import json
import sys

from kissa_lot.orchestrator import run_development


def main() -> int:
    parser = argparse.ArgumentParser(description="Kissa Lot development desk")
    parser.add_argument("source", nargs="?", help="Path to a screenplay or treatment")
    parser.add_argument("--title", default="")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.source:
        with open(args.source, encoding="utf-8") as fh:
            raw = fh.read()
    else:
        raw = sys.stdin.read()

    result = run_development(raw, title_hint=args.title, progress=lambda m: print(m, file=sys.stderr))
    if args.json:
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        return 0

    packet = result.packet
    print(f"\n{packet.working_title}")
    print(packet.polished_logline)
    print(f"\nVerdict: {packet.greenlight_verdict}  (confidence {packet.confidence})")
    print(f"Complexity: {result.complexity.score}/100 — {result.complexity.verdict}")
    print(f"Engines: {result.engines}")
    print("\nAudience desire\n" + packet.audience_desire)
    print("\nWhy now\n" + packet.why_now)
    if packet.clip_moments:
        print("\nClip moments")
        for item in packet.clip_moments:
            print(f"  • {item}")
    if result.complexity.cuts:
        print("\nCut list")
        for item in result.complexity.cuts:
            print(f"  • {item}")
    print("\nCitations")
    for hit in packet.citations[:8]:
        print(f"  • {hit.title} — {hit.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
