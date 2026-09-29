"""01 - Log Parser: reference solution."""
import re
from collections import Counter, defaultdict
from collections.abc import Iterable
from datetime import datetime

# One anchored regex validates the overall structure. Anything that doesn't match is malformed.
LINE_RE = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ \[(?P<ts>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<target>\S+) \S+" (?P<status>\d{3}) (?P<size>\d+|-)$'
)


def parse_line(line: str) -> dict | None:
    m = LINE_RE.match(line.strip())
    if not m:
        return None
    try:
        # The regex can't validate dates, so strptime does it (e.g. "99/Foo/2024").
        timestamp = datetime.strptime(m["ts"], "%d/%b/%Y:%H:%M:%S %z")
    except ValueError:
        return None
    return {
        "ip": m["ip"],
        "timestamp": timestamp,
        "method": m["method"],
        "path": m["target"].partition("?")[0],
        "status": int(m["status"]),
        "size": 0 if m["size"] == "-" else int(m["size"]),
    }


def summarize(lines: Iterable[str], top_n: int = 3) -> dict:
    total = malformed = errors = 0
    statuses: Counter[int] = Counter()
    ips: Counter[str] = Counter()
    by_path: defaultdict[str, int] = defaultdict(int)

    for line in lines:  # a single pass, so this works for generators and files too
        if not line.strip():
            continue
        if (rec := parse_line(line)) is None:
            malformed += 1
            continue
        total += 1
        statuses[rec["status"]] += 1
        ips[rec["ip"]] += 1
        by_path[rec["path"]] += rec["size"]
        errors += rec["status"] >= 400

    return {
        "total_requests": total,
        "malformed": malformed,
        "status_counts": dict(statuses),
        # Counter.most_common doesn't break ties deterministically, so sort explicitly.
        "top_ips": sorted(ips.items(), key=lambda kv: (-kv[1], kv[0]))[:top_n],
        "bytes_by_path": dict(by_path),
        "error_rate": round(errors / total, 4) if total else 0.0,
    }
