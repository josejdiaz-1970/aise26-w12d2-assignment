import logging
import sys


def setup_logging(log_level: str):
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Reduce noisy logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)