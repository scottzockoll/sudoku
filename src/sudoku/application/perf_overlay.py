from __future__ import annotations

import time


class PerfOverlay:
    def __init__(self) -> None:
        self.enabled = False
        self._frame_count = 0
        self._draw_count = 0
        self._skip_count = 0
        self._last_time = time.monotonic()
        self._fps = 0.0
        self._update_interval = 1.0

    def toggle(self) -> None:
        self.enabled = not self.enabled

    def record_frame(self, drew: bool) -> None:
        self._frame_count += 1
        if drew:
            self._draw_count += 1
        else:
            self._skip_count += 1

        now = time.monotonic()
        elapsed = now - self._last_time
        if elapsed >= self._update_interval:
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._draw_count = 0
            self._skip_count = 0
            self._last_time = now

    @property
    def fps(self) -> float:
        return self._fps

    @property
    def draw_count(self) -> int:
        return self._draw_count

    @property
    def skip_count(self) -> int:
        return self._skip_count
