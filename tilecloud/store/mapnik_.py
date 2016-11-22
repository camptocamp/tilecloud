from json import dumps

from tilecloud import TileStore

try:
    import mapnik2 as mapnik
    mapnik  # suppress pyflakes warning
except:
    import mapnik


class MapnikTileStore(TileStore):
    """
    Tile store that renders tiles with Mapnik

    requires mapnik2: http://pypi.python.org/pypi/mapnik2
    """

    def __init__(
            self, tilegrid, mapfile, data_buffer=128, image_buffer=0, output_format='png256', resolution=2,
            layers_fields=None, drop_empty_utfgrid=False, proj4_literal=None, **kwargs):
        """
        Constructs a MapnikTileStore

        :param tilegrid: the tilegrid.
        :param mapfile: the file used to render the tiles.
        :param buffer_size: the image buffer size default is 128.
        :param output_format: the output format,
            possible values 'jpeg', 'png', 'png256', 'grid',
            default is 'png256'
        :param layers: the layers and fields used in the grid generation,
            example: { 'my_layer': ['my_first_field', 'my_segonf_field']},
            default is {}.
        :param **kwargs: for extended class.
        """
        if layers_fields is None:
            layers_fields = {}

        TileStore.__init__(self, **kwargs)
        self.tilegrid = tilegrid
        self.buffer = image_buffer
        self.output_format = output_format
        self.resolution = resolution
        self.layers_fields = layers_fields
        self.drop_empty_utfgrid = drop_empty_utfgrid

        self.mapnik = mapnik.Map(tilegrid.tile_size, tilegrid.tile_size)
        mapnik.load_map(self.mapnik, mapfile, True)
        self.mapnik.buffer_size = data_buffer
        if proj4_literal is not None:
            self.mapnik.srs = proj4_literal

    def get_one(self, tile):
        bbox = self.tilegrid.extent(tile.tilecoord, self.buffer)
        bbox2d = mapnik.Box2d(bbox[0], bbox[1], bbox[2], bbox[3])

        size = tile.tilecoord.n * self.tilegrid.tile_size + 2 * self.buffer
        self.mapnik.resize(size, size)
        self.mapnik.zoom_to_box(bbox2d)

        if self.output_format == 'grid':
            grid = mapnik.Grid(self.tilegrid.tile_size, self.tilegrid.tile_size)
            for n, l in enumerate(self.mapnik.layers):
                if l.name in self.layers_fields:
                    mapnik.render_layer(self.mapnik, grid, layer=n, fields=self.layers_fields[l.name])

            encode = grid.encode('utf', resolution=self.resolution)
            if self.drop_empty_utfgrid and len(encode['data'].keys()) == 0:
                return None
            tile.data = dumps(encode)
        else:
            # Render image with default Agg renderer
            im = mapnik.Image(size, size)
            mapnik.render(self.mapnik, im)
            tile.data = im.tostring(self.output_format)

        return tile
