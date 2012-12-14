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
		<title>OpenLayers - TileCloud</title>
	</head>
	<body>
		<div id="map" style="width: 100%; height: 100%;">
		</div>
		<script type="text/javascript">
			var map = new OpenLayers.Map({
				div: "map",
%if max_extent:
				maxExtent: new OpenLayers.Bounds({{max_extent}}),
%end
%if resolutions:
				resolutions: [{{resolutions}}],
				maxResolution: 'auto',
%end
				allOverlays: true
			});
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
			map.addLayer(new OpenLayers.Layer.XYZ('{{name}}', '/tiles/{{index}}/tiles/${z}/${x}/${y}', {
%if getattr(tilestore, 'attribution', None):
				attribution: '{{!tilestore.attribution}}',
%end
				transitionEffect: 'resize',
%if max_extent or resolutions:
%pass
%else:
				numZoomLevels: 32,
				sphericalMercator: true
%end
			}));
%end
%end
%if len(tilestores) > 1:
			map.addControl(new OpenLayers.Control.LayerSwitcher());
%end
			map.zoomToMaxExtent();
		</script>
	</body>
</html>
