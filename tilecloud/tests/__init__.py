import logging
import sys

logging.basicConfig(
    level=logging.DEBUG,
    format="TEST       | %(asctime)-15s %(levelname)5s %(name)s %(message)s",
    stream=sys.stdout,
)
