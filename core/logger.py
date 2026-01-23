import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)

logger = logging.getLogger("applyra")

def log_event(event: dict):
    logger.info(json.dumps(event))
