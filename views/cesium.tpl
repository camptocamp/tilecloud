<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
		<script type="text/javascript" src="/static/Cesium.js"></script>
		<style type="text/css">
			html, body {
				margin: 0;
				padding: 0;
				height: 100%;
			}
			.fullSize {
				display: block;
				position: absolute;
				top: 0;
				left: 0;
				border: none;
				width: 100%;
				height: 100%;
				z-index: -1;
			}
		</style>
		<title>Cesium - TileCloud</title>
	</head>
	<body>
		<div id="cesiumContainer" class="fullSize">
		</div>
		<script type="text/javascript">

			// http://cesium.agi.com/Cesium/Apps/Sandcastle/index.html?src=Minimalist.html

			var canvas = document.createElement('canvas');
			canvas.className = 'fullSize';
			document.getElementById('cesiumContainer').appendChild(canvas);
			var ellipsoid = Cesium.Ellipsoid.WGS84;
			var scene = new Cesium.Scene(canvas);
			var primitives = scene.getPrimitives();
			var cb = new Cesium.CentralBody(ellipsoid);
			var imageryProvider;
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
			imageryProvider = new Cesium.OpenStreetMapImageryProvider({
%if getattr(tilestore, 'attribution', None):
				credit: '{{!tilestore.attribution}}',
%else:
				credit: '',
%end
				url:  '/tiles/{{index}}/tiles/'
			});
			cb.getImageryLayers().addImageryProvider(imageryProvider);
%end
%end
			primitives.setCentralBody(cb);
			scene.getCamera().getControllers().addCentralBody();

			function tick() {
				scene.render();
				Cesium.requestAnimationFrame(tick);
			}
			tick();

			var onResize = function() {
				var width = canvas.clientWidth;
				var height = canvas.clientHeight;
				if (canvas.width === width && canvas.height === height) {
					return;
				}
				canvas.width = width;
				canvas.height = height;
				scene.getCamera().frustum.aspectRatio = width / height;
			}
			window.addEventListener('resize', onResize, false);
			onResize();

		</script>
	</body>
</html>
