# Copyright (c) 2024-2026 Camptocamp
from tilecloud.grid.quad import QuadTileGrid

GoogleTileGrid = QuadTileGrid(
    max_extent=(-20037508.34, -20037508.34, 20037508.34, 20037508.34),
    tile_size=256,
)
