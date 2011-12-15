<!doctype html>
<html>
	<head>
		<title>TileCloud</title>
	</head>
	<body>
		<ul>
			<li><a href="/openlayers{{ '?debug=1' if debug else '' }}">OpenLayers</a></li>
			<li><a href="/leaflet{{ '?debug=1' if debug else '' }}">Leaflet</a></li>
			<li><a href="/openwebglobe{{ '?debug=1' if debug else '' }}">OpenWebGlobe</a></li>
		</ul>
	</body>
</html>
