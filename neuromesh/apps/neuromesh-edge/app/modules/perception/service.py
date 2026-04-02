from __future__ import annotations

from app.config import CameraConfig
from app.modules.perception.providers.base import PerceptionProvider
from app.modules.perception.providers.opencv_motion import OpenCVMotionProvider
from app.modules.perception.providers.simulated import SimulatedPerceptionProvider


class PerceptionService:
    def __init__(self, provider: PerceptionProvider) -> None:
        self.provider = provider

    @classmethod
    def build(cls, camera: CameraConfig, logger: object) -> "PerceptionService":
        if camera.enabled:
            try:
                provider = OpenCVMotionProvider(
                    device=camera.device,
                    width=camera.width,
                    height=camera.height,
                    fps=camera.fps,
                    logger=logger,
                )
                logger.info_json("perception_provider_selected", extra={"provider": provider.name, "device": camera.device})
                return cls(provider=provider)
            except Exception as exc:
                logger.warning_json("perception_provider_error", extra={"provider": "opencv_motion", "error": str(exc)})
                if not camera.simulation_fallback:
                    raise

        provider = SimulatedPerceptionProvider()
        logger.info_json("perception_provider_selected", extra={"provider": provider.name})
        return cls(provider=provider)

    def next_event(self, current_moving: bool):
        return self.provider.next_event(current_moving)

    def health(self) -> dict[str, object]:
        return self.provider.health()

    def close(self) -> None:
        self.provider.close()
