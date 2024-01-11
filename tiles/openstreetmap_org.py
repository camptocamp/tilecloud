from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore

tilestore = URLTileStore(
    (
        TemplateTileLayout(f"https://{server!s}.tile.openstreetmap.org/%(z)d/%(x)d/%(y)d.png")
        for server in "abc"
    ),
    attribution="&copy; OpenStreetMap contributors, CC-BY-SA",
    content_type="image/png",
    headers={"User-Agent": "TileCloud"},
)
