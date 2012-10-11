from tilecloud.store.wmts import WMTSTileStore


tilestore = WMTSTileStore(
    url='http://v2.suite.opengeo.org/geoserver/gwc/service/wmts/',
    layer='medford:buildings',
    style='_null',
    format='image/png',
    tile_matrix_set='EPSG:900913',
    tile_matrix=lambda z: 'EPSG:900913:%d' % (z,))
