from math import ceil
from typing import TypedDict, cast

from bottle import jinja2_template
from pyproj import Proj, transform

from tilecloud.lib.wmts_get_capabilities_template import WMTS_GET_CAPABILITIES_TEMPLATE

METERS_PER_UNIT = {"feet": 3.28084, "meters": 1, "degrees": 111118.752, "inch": 39.3700787}


def _to_wsg84(srs: str, x: float, y: float) -> tuple[float, float]:  # pylint: disable=invalid-name
    return cast(
        "tuple[float, float]",
        transform(Proj(init=srs.lower()), Proj(proj="latlong", datum="WGS84"), x, y),
    )


class _TileMatrixSet(TypedDict):
    name: str
    srs: str
    units: str
    resolutions: list[float]
    bbox: tuple[float, float, float, float]
    tile_size: int
    yorigin: str


class _Matrix(TypedDict):
    id: int
    tilewidth: int
    tileheight: int
    matrixwidth: int
    matrixheight: int
    resolution: float
    # 0.000028 corresponds to 0.28 mm per pixel
    scale: float
    topleft: str


class _MatrixSet(TypedDict):
    crs: str
    matrices: list[_Matrix]


def _matrix_sets(tile_matrix_set: _TileMatrixSet) -> dict[str, _MatrixSet]:
    sets: dict[str, _MatrixSet] = {}
    tile_size = int(tile_matrix_set["tile_size"])
    units = tile_matrix_set["units"]
    matrix_set: _MatrixSet = {"crs": tile_matrix_set["srs"].replace(":", "::"), "matrices": []}
    for i, resolution in enumerate(tile_matrix_set["resolutions"]):
        col = ceil(((tile_matrix_set["bbox"][2] - tile_matrix_set["bbox"][0]) / tile_size) / resolution)
        row = ceil(((tile_matrix_set["bbox"][3] - tile_matrix_set["bbox"][1]) / tile_size) / resolution)
        if tile_matrix_set.get("yorigin", "bottom") == "top":
            maxy = tile_matrix_set["bbox"][1]
        else:
            maxy = tile_matrix_set["bbox"][1] + (row * tile_size * resolution)

        matrix: _Matrix = {
            "id": i,
            "tilewidth": tile_size,
            "tileheight": tile_size,
            "matrixwidth": col,
            "matrixheight": row,
            "resolution": resolution,
            # 0.000028 corresponds to 0.28 mm per pixel
            "scale": resolution * METERS_PER_UNIT[units] / 0.00028,
            "topleft": f"{tile_matrix_set['bbox'][0]:f} {maxy:f}",
        }
        matrix_set["matrices"].append(matrix)
    sets[tile_matrix_set["name"]] = matrix_set

    return sets


class _Layer(TypedDict):
    """Layer definition for the WMTS GetCapabilities XML."""

    extension: str
    dimension_key: str
    dimension_default: str
    dimension_values: list[str]
    matrix_set: str


def _get_capabilities(layers: list[_Layer], tile_matrix_set: _TileMatrixSet, wmts_gettile: str) -> str:
    """
    Generate the WMTS GetCapabilities XML.

    Layers is an array of dict that contains:

    extension: the tiles extension like 'png'
        dimension_key: the used dimension key
        dimension_default: the default dimension value
        dimension_values: the possible dimension value
        matrix_set: the matrix set name
    tile_matrix_set a dict that constants the tile matrix set definition:
        name: the name of the tile matrix set
        srs: projection like 'EPSG:21781'
        units: units like 'meters'
        resolutions: array of floats for used resolutions
        bbox: array of floats, the use bbox where the tiles is generated
        tile_size: the size of the tiles (int)
        yorigin: 'top' if the tiles origin is at top
    """
    return cast(
        "str",
        jinja2_template(
            WMTS_GET_CAPABILITIES_TEMPLATE,
            layers=layers,
            matrix_sets=_matrix_sets(tile_matrix_set),
            wmts_gettile=wmts_gettile,
            tile_matrix_set=tile_matrix_set["name"],
        ),
    )
