# 01 · Log Parser  (Easy)

**Skills:** string parsing, regex, `datetime`, `collections.Counter`, handling bad input

You are given web-server access logs in a simplified Common Log Format:

```
192.168.1.10 - - [10/Oct/2023:13:55:36 +0000] "GET /index.html HTTP/1.1" 200 2326
```

Fields: `ip`, two ignored `-` fields, `[timestamp]`, `"METHOD PATH PROTOCOL"`, `status`, `size`.

## Part 1 — `parse_line(line)`

Return a dict:

| key         | type                     | notes                                                   |
|-------------|--------------------------|---------------------------------------------------------|
| `ip`        | `str`                    | first token                                             |
| `timestamp` | timezone-aware `datetime`| format `%d/%b/%Y:%H:%M:%S %z`                           |
| `method`    | `str`                    | e.g. `"GET"`                                            |
| `path`      | `str`                    | **without** any query string (`/search?q=x` → `/search`)|
| `status`    | `int`                    | 3-digit status code                                     |
| `size`      | `int`                    | `-` means `0`                                           |

- Ignore surrounding whitespace, including a trailing newline.
- If the line is malformed in **any** way (wrong structure, bad date, non-numeric
  status/size), return `None`. Don't raise.

## Part 2 — `summarize(lines, top_n=3)`

`lines` is any iterable of strings. It could be a list, a generator, or an open file.
Blank or whitespace-only lines are skipped completely and don't count as malformed.

Return:

```python
{
    "total_requests": int,          # number of valid lines
    "malformed": int,               # number of non-blank lines that failed to parse
    "status_counts": {200: 5, ...}, # int status -> count
    "top_ips": [("1.2.3.4", 7), ...],  # top_n by count desc, ties broken by ip asc
    "bytes_by_path": {"/a": 1234},  # total size per path (query string stripped)
    "error_rate": float,            # fraction of valid requests with status >= 400,
                                    # rounded to 4 dp; 0.0 if there are no requests
}
```

Run the tests:

```bash
pipenv run pytest 01_log_parser
```
