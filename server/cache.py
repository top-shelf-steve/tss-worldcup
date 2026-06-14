"""In-memory dataset cache with a background refresh thread and disk fallback.

Mirrors the resilience pattern from the other trackers: serve the last good
data even if a refresh fails, and survive a restart by loading the on-disk copy
written after each successful build.
"""

import json
import threading
import time
from pathlib import Path

from . import dataset as dataset_mod

DISK_PATH = Path(__file__).resolve().parent.parent / "data" / "cache.json"


class DataCache:
    def __init__(self, source, refresh_seconds: int = 600):
        self.source = source
        self.refresh_seconds = refresh_seconds
        self._lock = threading.Lock()
        self._dataset = None
        self._updated_at = None
        self._error = None
        self._load_from_disk()

    # --- public ---------------------------------------------------------
    @property
    def dataset(self):
        with self._lock:
            return self._dataset

    def status(self) -> dict:
        with self._lock:
            return {
                "source": self.source.name,
                "updated_at": self._updated_at,
                "stale": self._dataset is None,
                "last_error": self._error,
                "refresh_seconds": self.refresh_seconds,
            }

    def refresh(self) -> bool:
        """Fetch + rebuild. Keep prior data on failure. Returns success."""
        try:
            ds = dataset_mod.build(self.source)
        except Exception as exc:  # noqa: BLE001 - keep serving last good data
            with self._lock:
                self._error = f"{type(exc).__name__}: {exc}"
            return False
        with self._lock:
            self._dataset = ds
            self._updated_at = ds["generated_at"]
            self._error = None
        self._save_to_disk(ds)
        return True

    def start_background(self):
        t = threading.Thread(target=self._loop, name="wc-refresh", daemon=True)
        t.start()

    # --- internals ------------------------------------------------------
    def _loop(self):
        while True:
            self.refresh()
            time.sleep(self.refresh_seconds)

    def _load_from_disk(self):
        try:
            ds = json.loads(DISK_PATH.read_text(encoding="utf-8"))
            self._dataset = ds
            self._updated_at = ds.get("generated_at")
        except (OSError, ValueError):
            pass

    def _save_to_disk(self, ds: dict):
        try:
            DISK_PATH.parent.mkdir(parents=True, exist_ok=True)
            DISK_PATH.write_text(json.dumps(ds), encoding="utf-8")
        except OSError:
            pass
