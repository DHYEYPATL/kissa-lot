from __future__ import annotations

import json
import sys

from qissa.eval_harness import run_eval
from qissa.pipeline import run_desk


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        print(json.dumps(run_eval(), indent=2))
        return 0
    seed = (
        sys.stdin.read().strip()
        if not sys.stdin.isatty()
        else "A night-shift cook in Surat keeps her late mother's recipe book taped under a prep table."
    )
    state = run_desk(seed)
    print(json.dumps(state.model_dump(), indent=2, ensure_ascii=False)[:8000])
    print(f"\n{state.verdict}  status={state.status}  cycle={state.cycle}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
