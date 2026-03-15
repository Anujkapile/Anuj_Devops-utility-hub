import re
from collections import Counter
from datetime import datetime

# Common log level patterns
LOG_LEVEL_PATTERN = re.compile(
    r"\b(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|FATAL|TRACE|NOTICE)\b",
    re.IGNORECASE,
)

# Common timestamp patterns
TIMESTAMP_PATTERNS = [
    re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}"),   # ISO 8601
    re.compile(r"\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}"),        # Apache
    re.compile(r"\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}"),        # syslog
]

LEVEL_ALIASES = {
    "WARN": "WARNING",
    "FATAL": "CRITICAL",
}

SEVERITY_ORDER = {"DEBUG": 0, "TRACE": 0, "INFO": 1, "NOTICE": 1,
                  "WARNING": 2, "ERROR": 3, "CRITICAL": 4}


def _normalize_level(level: str) -> str:
    return LEVEL_ALIASES.get(level.upper(), level.upper())


def _extract_level(line: str) -> str | None:
    match = LOG_LEVEL_PATTERN.search(line)
    if match:
        return _normalize_level(match.group(1))
    return None


def _extract_timestamp(line: str) -> str | None:
    for pattern in TIMESTAMP_PATTERNS:
        match = pattern.search(line)
        if match:
            return match.group(0)
    return None


def analyze_logs(
    log_text: str,
    level_filter: str = "ALL",
    keyword: str = "",
) -> dict:
    """
    Parse raw log text and return structured entries + statistics.

    Args:
        log_text:     Raw multi-line log content.
        level_filter: Return only lines at or above this severity (ALL = no filter).
        keyword:      Optional substring filter applied after level filter.

    Returns:
        {
          "entries": [...],
          "stats":   {...},
          "filtered_count": int,
          "total_count": int,
        }
    """
    lines = log_text.splitlines()
    entries = []
    level_counts: Counter = Counter()

    for line_no, raw_line in enumerate(lines, start=1):
        line = raw_line.rstrip()
        if not line:
            continue

        level = _extract_level(line) or "UNKNOWN"
        timestamp = _extract_timestamp(line)
        level_counts[level] += 1

        entries.append(
            {
                "line_no": line_no,
                "timestamp": timestamp,
                "level": level,
                "message": line,
            }
        )

    # Apply level filter
    min_severity = SEVERITY_ORDER.get(level_filter.upper(), -1)
    if level_filter.upper() != "ALL" and min_severity >= 0:
        entries = [
            e for e in entries
            if SEVERITY_ORDER.get(e["level"], -1) >= min_severity
        ]

    # Apply keyword filter
    if keyword.strip():
        kw_lower = keyword.strip().lower()
        entries = [e for e in entries if kw_lower in e["message"].lower()]

    stats = {
        "level_counts": dict(level_counts),
        "total_lines": len(lines),
        "non_empty_lines": sum(1 for l in lines if l.strip()),
        "error_rate": round(
            (level_counts.get("ERROR", 0) + level_counts.get("CRITICAL", 0))
            / max(len(entries), 1)
            * 100,
            2,
        ),
    }

    return {
        "entries": entries,
        "stats": stats,
        "filtered_count": len(entries),
        "total_count": stats["non_empty_lines"],
    }


def get_log_summary(log_text: str) -> dict:
    """
    Return a high-level summary of the log: counts per level, first/last
    timestamp, top repeated messages, and detected anomalies.
    """
    result = analyze_logs(log_text)
    entries = result["entries"]

    timestamps = [e["timestamp"] for e in entries if e["timestamp"]]
    message_counter = Counter(e["message"] for e in entries)
    top_messages = [
        {"message": msg, "count": cnt}
        for msg, cnt in message_counter.most_common(10)
        if cnt > 1
    ]

    # Simple anomaly detection: runs of consecutive errors
    anomalies = []
    consecutive = 0
    for e in entries:
        if e["level"] in ("ERROR", "CRITICAL"):
            consecutive += 1
            if consecutive >= 3:
                anomalies.append(
                    f"Error burst detected near line {e['line_no']}"
                )
        else:
            consecutive = 0
    # Deduplicate anomaly messages
    anomalies = list(dict.fromkeys(anomalies))

    return {
        "level_counts": result["stats"]["level_counts"],
        "total_lines": result["stats"]["non_empty_lines"],
        "first_timestamp": timestamps[0] if timestamps else None,
        "last_timestamp": timestamps[-1] if timestamps else None,
        "top_repeated_messages": top_messages,
        "anomalies": anomalies[:5],
        "error_rate_pct": result["stats"]["error_rate"],
    }
