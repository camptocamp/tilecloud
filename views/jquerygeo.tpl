<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
		<script src="http://code.jquery.com/jquery-1.7.1.min.js"></script>
		<script src="http://code.jquerygeo.com/jquery.geo-1.0a4.min.js"></script>
		<style type="text/css">
			html, body, #map {
				margin: 0;
				padding: 0;
				height: 100%;
			}
		</style>
		<title>jQueryGeo - TileCloud</title>
	</head>
	<body>
		<div id="map" style="width: 100%; height: 100%;">
		</div>
		<script>
			$(function () {
				var services = [];
%for index, (name, tile_store) in enumerate(tile_stores):
%if tile_store.content_type is None or tile_store.content_type.startswith('image/'):
				services.push({
					id: "{{name}}",
%if getattr(tile_store, 'attribution', None):
					attr: '{{!tile_store.attribution}}',
%end
					src: function( view ) {
						return "/tiles/{{index}}/tiles/" + view.zoom + "/" + view.tile.column + "/" + view.tile.row;
					},
					type: "tiled"
				});
%end
%end
				var map = $( "#map" ).geomap( {
					services: services
				} );
			});
		</script>
	</body>
</html>
