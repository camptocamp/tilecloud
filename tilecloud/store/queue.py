import base64
import json
from typing import Any

from tilecloud import Tile, TileCoord


def encode_message(tile: Tile) -> str:
    """Encode a tile to a string message."""
    metadata = dict(tile.metadata)
    metadata.pop("sqs_message", None)
    message = {
        "z": tile.tilecoord.z,
        "x": tile.tilecoord.x,
        "y": tile.tilecoord.y,
        "n": tile.tilecoord.n,
        "metadata": metadata,
    }

    return base64.b64encode(json.dumps(message).encode("utf-8")).decode("utf-8")


def decode_message(text: str, **kwargs: Any) -> Tile:
    """Decode a tile from a string message."""
    body = json.loads(base64.b64decode(text).decode("utf-8"))
    z = body.get("z")  # pylint: disable=invalid-name
    x = body.get("x")  # pylint: disable=invalid-name
    y = body.get("y")  # pylint: disable=invalid-name
    n = body.get("n")  # pylint: disable=invalid-name
    metadata = body.get("metadata", {})
    return Tile(TileCoord(z, x, y, n), metadata=metadata, **kwargs)
