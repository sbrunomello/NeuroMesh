from __future__ import annotations

from collections import deque
from typing import Any

from app.modules.perception.providers.base import PerceptionProvider


class OpenCVMotionProvider(PerceptionProvider):
    name = "opencv_motion"

    def __init__(self, *, device: str, width: int, height: int, fps: int, logger: object) -> None:
        self._logger = logger
        self._device = device
        self._width = width
        self._height = height
        self._fps = fps
        self._frames_processed = 0
        self._last_capture_ok = False
        self._recent_errors: deque[str] = deque(maxlen=5)

        try:
            import cv2  # type: ignore
        except Exception as exc:
            raise RuntimeError(f"opencv_import_failed:{exc}") from exc

        self._cv2 = cv2
        selected_device: Any = int(device) if str(device).isdigit() else device
        self._capture = cv2.VideoCapture(selected_device)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self._capture.set(cv2.CAP_PROP_FPS, fps)

        if not self._capture.isOpened():
            raise RuntimeError(f"camera_open_failed:{device}")

        self._background = self._cv2.createBackgroundSubtractorMOG2(history=150, varThreshold=25, detectShadows=False)
        self._logger.info_json("camera_opened", extra={"device": device, "width": width, "height": height, "fps": fps})

    def next_event(self, current_moving: bool) -> tuple[bool, float, float, dict[str, object]]:
        ok, frame = self._capture.read()
        self._last_capture_ok = bool(ok)
        if not ok or frame is None:
            self._recent_errors.append("capture_failed")
            raise RuntimeError("camera_capture_failed")

        self._frames_processed += 1
        fg = self._background.apply(frame)
        motion_pixels = int((fg > 200).sum())
        total_pixels = int(fg.size)
        ratio = motion_pixels / max(1, total_pixels)
        moving = ratio > 0.02
        confidence = round(min(0.99, ratio * 20), 2) if moving else round(max(0.01, ratio * 10), 2)
        meta = {
            "source": "camera",
            "frames_processed": self._frames_processed,
            "device": self._device,
            "frame_width": int(frame.shape[1]),
            "frame_height": int(frame.shape[0]),
            "motion_ratio": round(ratio, 4),
        }
        return moving, confidence, 0.0, meta

    def health(self) -> dict[str, object]:
        return {
            "provider": self.name,
            "camera_enabled": True,
            "device": self._device,
            "frames_processed": self._frames_processed,
            "last_capture_ok": self._last_capture_ok,
            "recent_errors": list(self._recent_errors),
        }

    def close(self) -> None:
        try:
            self._capture.release()
        except Exception:
            return None
