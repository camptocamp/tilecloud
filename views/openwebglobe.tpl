<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
		<script type="text/javascript" src="http://www.openwebglobe.org/beta/externals/openwebglobe_0.7.3.js"></script>
		<title>OpenWebGlobe - TileCloud</title>
	</head>
	<body>
		<div style="width: 100%; height: 100%;">
			<canvas id="canvas">
			</canvas>
		</div>
		<script type="text/javascript">
			ogSetArtworkDirectory('http://www.openwebglobe.org/art/');
			var context = ogCreateContextFromCanvas('canvas', true);
			var globe = ogCreateGlobe(context);
%for index, (name, tile_store) in enumerate(tile_stores):
%if tile_store.content_type == 'application/json':
			ogAddElevationLayer(globe, {
				url: ['/data/image'],
				layer: '{{index}}',
				service: 'owg'
			});
%else:
			ogAddImageLayer(globe, {
				url: ['/data/image'],
				layer: '{{index}}',
				service: 'owg'
			});
%end
%end
%if quality:
			var scene = ogGetScene(context);
			var world = ogGetWorld(scene);
			ogSetRenderQuality(world, {{quality}});
%end
		</script>
	</body>
</html>
