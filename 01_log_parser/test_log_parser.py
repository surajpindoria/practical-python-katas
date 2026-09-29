from datetime import datetime, timedelta, timezone

import pytest

from log_parser import parse_line, summarize

VALID = '192.168.1.10 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326'


# ---------------------------------------------------------------- parse_line

def test_parse_valid_line():
    assert parse_line(VALID) == {
        "ip": "192.168.1.10",
        "timestamp": datetime(2023, 10, 10, 13, 55, 36, tzinfo=timezone.utc),
        "method": "GET",
        "path": "/index.html",
        "status": 200,
        "size": 2326,
    }


def test_timestamp_is_timezone_aware_with_offset():
    line = '10.0.0.1 - - [01/Feb/2024:08:00:00 -0700] "POST /api HTTP/1.1" 201 10'
    ts = parse_line(line)["timestamp"]
    assert ts.utcoffset() == timedelta(hours=-7)
    assert ts == datetime(2024, 2, 1, 15, 0, 0, tzinfo=timezone.utc)


def test_trailing_newline_and_whitespace_ignored():
    assert parse_line("  " + VALID + "\n") == parse_line(VALID)


def test_dash_size_is_zero():
    line = '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "HEAD / HTTP/1.1" 304 -'
    assert parse_line(line)["size"] == 0


def test_query_string_is_stripped_from_path():
    line = '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "GET /search?q=python&page=2 HTTP/1.1" 200 99'
    assert parse_line(line)["path"] == "/search"


@pytest.mark.parametrize(
    "line",
    [
        "",
        "complete garbage",
        '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "GET / HTTP/1.1" 200',  # missing size
        '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "GET / HTTP/1.1" abc 12',  # bad status
        '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "GET / HTTP/1.1" 200 1x',  # bad size
        '10.0.0.1 - - [99/Foo/2024:08:00:00 +0000] "GET / HTTP/1.1" 200 12',  # bad date
        '10.0.0.1 - - 01/Feb/2024:08:00:00 +0000 "GET / HTTP/1.1" 200 12',  # no brackets
        '10.0.0.1 - - [01/Feb/2024:08:00:00 +0000] "GET" 200 12',  # bad request section
    ],
)
def test_malformed_lines_return_none(line):
    assert parse_line(line) is None


# ----------------------------------------------------------------- summarize

def _line(ip, path, status, size, method="GET"):
    return f'{ip} - - [10/Oct/2023:13:55:36 +0000] "{method} {path} HTTP/1.1" {status} {size}'


SAMPLE = [
    _line("1.1.1.1", "/", 200, 100),
    _line("2.2.2.2", "/about", 200, 50),
    _line("1.1.1.1", "/?ref=home", 200, 100),
    "not a log line",
    "",
    "   ",
    _line("3.3.3.3", "/missing", 404, "-"),
    _line("2.2.2.2", "/", 500, 10),
    _line("1.1.1.1", "/about", 301, 0),
    _line("4.4.4.4", "/", 200, 5),
]


def test_summarize_counts():
    s = summarize(SAMPLE)
    assert s["total_requests"] == 7
    assert s["malformed"] == 1
    assert s["status_counts"] == {200: 4, 404: 1, 500: 1, 301: 1}


def test_summarize_top_ips_sorted_with_tiebreak():
    s = summarize(SAMPLE)
    assert s["top_ips"] == [("1.1.1.1", 3), ("2.2.2.2", 2), ("3.3.3.3", 1)]


def test_summarize_custom_top_n():
    assert summarize(SAMPLE, top_n=1)["top_ips"] == [("1.1.1.1", 3)]
    assert len(summarize(SAMPLE, top_n=10)["top_ips"]) == 4


def test_summarize_bytes_by_path():
    assert summarize(SAMPLE)["bytes_by_path"] == {"/": 215, "/about": 50, "/missing": 0}


def test_summarize_error_rate():
    assert summarize(SAMPLE)["error_rate"] == round(2 / 7, 4)


def test_summarize_accepts_generator():
    s = summarize(line for line in SAMPLE)
    assert s["total_requests"] == 7


def test_summarize_reads_from_file(tmp_path):
    p = tmp_path / "access.log"
    p.write_text("\n".join(SAMPLE) + "\n")
    with p.open() as f:
        s = summarize(f)
    assert s["total_requests"] == 7
    assert s["malformed"] == 1


def test_summarize_empty():
    assert summarize([]) == {
        "total_requests": 0,
        "malformed": 0,
        "status_counts": {},
        "top_ips": [],
        "bytes_by_path": {},
        "error_rate": 0.0,
    }
