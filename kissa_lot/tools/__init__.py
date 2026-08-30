from kissa_lot.tools.complexity import score_complexity
from kissa_lot.tools.script_parse import parse_screenplay

__all__ = [
    "parse_screenplay",
    "score_complexity",
    "parallel_web_search",
    "research_story",
]


def __getattr__(name: str):
    if name in {"parallel_web_search", "research_story"}:
        from kissa_lot.tools import parallel_search

        return getattr(parallel_search, name)
    raise AttributeError(name)
