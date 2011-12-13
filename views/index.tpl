<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
%if debug:
		<link rel="stylesheet" href="/openlayers/theme/default/style.css" type="text/css">
		<script type="text/javascript" src="/openlayers/lib/OpenLayers.js"></script>
%else:
		<script type="text/javascript" src="/openlayers/build/OpenLayers.js"></script>
%end

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
				div: "map"
			});
%for index, name in enumerate(names):
			map.addLayer(new OpenLayers.Layer.XYZ('{{name}}', '/t/{{index}}/${z}/${x}/${y}', {
				sphericalMercator: true
			}));
%end
%if len(names) > 0:
			map.addControl(new OpenLayers.Control.LayerSwitcher());
%end
			map.addControl(new OpenLayers.Control.MousePosition());
			map.zoomToMaxExtent();
		</script>
	</body>
</html>
