import base64
import json
from typing import Any

from tilecloud import Tile, TileCoord


def encode_message(tile: Tile) -> str:
    metadata = dict(tile.metadata)
    if "sqs_message" in metadata:
        del metadata["sqs_message"]
    message = {
        "z": tile.tilecoord.z,
        "x": tile.tilecoord.x,
        "y": tile.tilecoord.y,
        "n": tile.tilecoord.n,
        "metadata": metadata,
    }

    return base64.b64encode(json.dumps(message).encode("utf-8")).decode("utf-8")


def decode_message(text: str, **kwargs: Any) -> Tile:
    body = json.loads(base64.b64decode(text).decode("utf-8"))
    z = body.get("z")
    x = body.get("x")
    y = body.get("y")
    n = body.get("n")
    metadata = body.get("metadata", {})
    return Tile(TileCoord(z, x, y, n), metadata=metadata, **kwargs)
