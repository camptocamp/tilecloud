<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
		<script type="text/javascript" src="http://www.openlayers.org/api/OpenLayers.js"></script>
		<style type="text/css">
			html, body, #map {
				margin: 0;
				padding: 0;
				height: 100%;
			}
		</style>
		<title>TileCloud</title>
	</head>
	<body>
		<div id="map" style="width: 100%; height: 100%;">
		</div>
		<script type="text/javascript">
			var map = new OpenLayers.Map({
				div: "map",
				allOverlays: true
			});
%for index, (name, tile_store) in enumerate(tile_stores):
%if tile_store.content_type is None or tile_store.content_type.startswith('image/'):
			map.addLayer(new OpenLayers.Layer.XYZ('{{name}}', '/data/image/{{index}}/tiles/${z}/${x}/${y}', {
%if getattr(tile_store, 'attribution', None):
				attribution: '{{!tile_store.attribution}}',
%end
				sphericalMercator: true
			}));
%end
%end
%if len(tile_stores) > 1:
			map.addControl(new OpenLayers.Control.LayerSwitcher());
%end
			map.zoomToMaxExtent();
		</script>
	</body>
</html>
