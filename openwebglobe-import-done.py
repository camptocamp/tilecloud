import sqlite3

from tilecloud import consume
from tilecloud.store.mbtiles import MBTilesTileStore

from tiles.map3d.lancer_17_transparent import tile_store as lancer_17_transparent_tile_store
from tiles.map3d.lancer_17_written import tile_store as lancer_17_written_tile_store

connection = sqlite3.connect('map3d.done.mbtiles')
done_tile_store = MBTilesTileStore(connection, commit=False)
for tile_store in [lancer_17_transparent_tile_store, lancer_17_written_tile_store]:
    tilestream = tile_store.list()
    tilestream = done_tile_store.put(tilestream)
    consume(tilestream, None)
    connection.commit()
