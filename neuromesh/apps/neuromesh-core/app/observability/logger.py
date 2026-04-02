from packages.observability.logging import get_logger


def build_logger():
    return get_logger("core-runtime")
