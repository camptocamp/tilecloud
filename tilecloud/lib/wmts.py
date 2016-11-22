from math import ceil

from bottle import jinja2_template
from pyproj import Proj, transform
from six import iteritems

from tilecloud.lib.wmts_get_capabilities_template import wmts_get_capabilities_template

METERS_PER_UNIT = {
    "feet": 3.28084,
    "meters": 1,
    "degrees": 111118.752,
    "inch": 39.3700787
}


def to_wsg84(srs, x, y):
    return transform(Proj(init=srs.lower()),
                     Proj(proj="latlong", datum="WGS84"), x, y)


def matrix_sets(tile_matrix_set):
    sets = {}
    tile_size = int(tile_matrix_set['tile_size'])
    units = tile_matrix_set['units']
    matrix_set = {"crs": tile_matrix_set['srs'].replace(':', '::'), "matrices": []}
    for i, resolution in enumerate(tile_matrix_set['resolutions']):
        col = int(ceil(((tile_matrix_set['bbox'][2] - tile_matrix_set['bbox'][0]) / tile_size) / resolution))
        row = int(ceil(((tile_matrix_set['bbox'][3] - tile_matrix_set['bbox'][1]) / tile_size) / resolution))
        if hasattr(tile_matrix_set, 'yorigin') and tile_matrix_set.yorigin == 'top':
            maxy = tile_matrix_set['bbox'][1]
        else:
            maxy = tile_matrix_set['bbox'][1] + (row * tile_size * resolution)

        matrix_set["matrices"].append({
            "id": i,
            "tilewidth": tile_size,
            "tileheight": tile_size,
            "matrixwidth": col,
            "matrixheight": row,
            "resolution": resolution,
            # 0.000028 corresponds to 0.28 mm per pixel
            "scale": resolution * METERS_PER_UNIT[units] / 0.00028,
            "topleft": "{0:f} {1:f}".format(tile_matrix_set['bbox'][0], maxy)
        })
    sets[tile_matrix_set['name']] = matrix_set

    return sets


def get_capabilities(layers, tile_matrix_set, wmts_gettile):
    """
    layers is an array of dict that contains:
        extension: the tiles extension like 'png'
        dimension_key: the used dimension key
        dimension_default: the default dimension value
        dimension_values: the possible dimension value
        matrix_set: the matrix set name
    tile_matrix_set a dict that contants the tile matrix set definition:
        name: the name of the tile matrix set
        srs: projection like 'EPSG:21781'
        units: units like 'meters'
        resolutions: array of floats for used resolutions
        bbox: array of floats, the use bbox where the tiles is generated
        tiles_size: the sise of the tiles (int)
        yorigin: 'top' if the tiles origin is at top
    """
    return jinja2_template(
        wmts_get_capabilities_template,
        layers=layers,
        matrix_sets=matrix_sets(tile_matrix_set),
        wmts_gettile=wmts_gettile,
        tile_matrix_set=tile_matrix_set['name'],
        iteritems=iteritems)
