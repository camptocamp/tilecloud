# https://github.com/mapbox/TileJSON

import json
import mimetypes
import os.path
import re
from urlparse import urlparse

from tilecloud import BoundingPyramid
from tilecloud.layout.template import TemplateTileLayout
from tilecloud.store.url import URLTileStore



class TileJSONTileStore(URLTileStore):

    def __init__(self, tile_json, urls_key='tiles', **kwargs):
        # FIXME schema
        # FIXME version 1.0.0 support
        d = json.loads(tile_json)
        assert 'tiles' in d
        assert isinstance(d['tiles'], list)
        assert len(d['tiles']) > 0
        for key in 'name description version attribution template legend center'.split():
            kwargs.setdefault(key, d.get(key, None))
        if 'bounding_pyramid' not in kwargs:
            zmin, zmax = d.get('minzoom', 0), d.get('maxzoom', 22)
            if 'bounds' in d:
                xmin, ymin, xmax, ymax = d['bounds']
                bounding_pyramid = BoundingPyramid.from_spherical_mercator(zmin, zmax, xmin, xmax, ymin, ymax)
            else:
                bounding_pyramid = BoundingPyramid.full(zmin, zmax)
            kwargs['bounding_pyramid'] = bounding_pyramid
        urls = d[urls_key]
        if 'content_type' not in kwargs:
            exts = set(os.path.splitext(urlparse(url).path)[1] for url in urls)
            content_types = set(mimetypes.types_map.get(ext) for ext in exts)
            assert len(content_types) == 1
            kwargs['content_type'] = content_types.pop()
        templates = [re.sub(r'\{([xyz])\}', lambda m: '%%(%s)d' % m.group(1), url) for url in urls]
        tile_layouts = map(TemplateTileLayout, templates)
        URLTileStore.__init__(self, tile_layouts, **kwargs)
