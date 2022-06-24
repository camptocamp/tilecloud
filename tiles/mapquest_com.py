from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore

tilestore = URLTileStore(
    (
        TemplateTileLayout(f"http://otile{i:d}.mqcdn.com/tiles/1.0.0/osm/%(z)d/%(x)d/%(y)d.png")
        for i in range(1, 5)
    ),
    attribution=(
        "Data, imagery and map information provided by MapQuest, "
        '<a href="http://www.openstreetmap.org/">Open Street Map</a> and contributors, '
        '<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>.'
    ),
    content_type="image/png",
)
