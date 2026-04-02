from __future__ import annotations

from dataclasses import dataclass

from app.client.edge_client import EdgeClient
from app.observability.logger import build_logger


@dataclass
class CoreContext:
    edge_client: EdgeClient
    logger: object


def build_context() -> CoreContext:
    logger = build_logger()
    return CoreContext(edge_client=EdgeClient(logger), logger=logger)
