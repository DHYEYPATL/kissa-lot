from __future__ import annotations

import os
from typing import Any


def parallel_search(objective: str, queries: list[str]) -> list[dict[str, Any]]:
    api_key = os.environ.get("PARALLEL_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("PARALLEL_API_KEY missing")
    from parallel import Parallel

    client = Parallel(api_key=api_key)
    search = client.search(
        objective=objective,
        search_queries=queries[:5],
        mode=os.environ.get("PARALLEL_SEARCH_MODE", "fast"),
    )
    hits = []
    for item in getattr(search, "results", None) or []:
        hits.append(
            {
                "title": getattr(item, "title", "") or "",
                "url": getattr(item, "url", "") or "",
                "publish_date": str(getattr(item, "publish_date", "") or ""),
                "excerpts": list(getattr(item, "excerpts", None) or [])[:3],
            }
        )
    return hits
