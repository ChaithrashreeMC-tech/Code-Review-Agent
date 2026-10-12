# TC-003: Memory and Resource Management (PERF03 violation)
# Expected: PERF03 finding, severity=high, confidence=high
# Technology: Python

import csv
import io
from typing import Generator, Iterator
from sqlalchemy.orm import Session
from models import LogEntry


# --- VIOLATION: Unbounded buffering of large dataset ---
def export_logs_to_csv_buffered(db: Session) -> bytes:
    """
    VIOLATION: Fetches ALL log entries into memory, then builds the CSV
    in memory as a single bytes object. On a production system with millions
    of log entries this will OOM the service.
    """
    entries = db.query(LogEntry).all()  # VIOLATION: unbounded .all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "timestamp", "level", "message"])
    for entry in entries:
        writer.writerow([entry.id, entry.timestamp, entry.level, entry.message])

    return output.getvalue().encode("utf-8")  # VIOLATION: all data in RAM


# --- VIOLATION: Missing resource disposal ---
def read_config_no_close(path: str) -> str:
    """
    VIOLATION: File handle is never closed. In a long-running service,
    repeated calls will exhaust file descriptors.
    """
    f = open(path, "r")   # VIOLATION: no context manager / close()
    return f.read()


# --- SAFE: Streaming generator ---
def export_logs_to_csv_streaming(db: Session) -> Generator[bytes, None, None]:
    """
    SAFE: Uses yield_per() to fetch rows in batches, and yields CSV chunks
    to the caller. Memory usage is bounded by the batch size, not the
    total dataset size.
    """
    yield b"id,timestamp,level,message\n"
    for entry in db.query(LogEntry).yield_per(1000):  # batch of 1000 rows
        row = f"{entry.id},{entry.timestamp},{entry.level},{entry.message}\n"
        yield row.encode("utf-8")


# --- SAFE: Proper resource disposal ---
def read_config_safe(path: str) -> str:
    """
    SAFE: Context manager guarantees the file handle is closed even if an
    exception occurs.
    """
    with open(path, "r") as f:
        return f.read()


# NOT APPLICABLE: Small bounded file — buffering is fine
def load_app_config(path: str = "config.json") -> dict:
    """
    NOT APPLICABLE: config.json is always small (< 4 KB).
    Reading it fully into memory is not a resource concern.
    PERF03 should not be flagged here.
    """
    import json
    with open(path, "r") as f:
        return json.load(f)

