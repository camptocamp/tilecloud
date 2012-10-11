from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore


tilestore = URLTileStore(
    (TemplateTileLayout('http://%s.tile.openstreetmap.org/%%(z)d/%%(x)d/%%(y)d.png' % server) for server in 'abc'),
    attribution='&copy; OpenStreetMap contributors, CC-BY-SA', content_type='image/png')
