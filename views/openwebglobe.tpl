<!doctype html>
<html>
	<head>
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
		<meta name="viewport" content="initial-scale=1.0, user-scalable=no">
%if debug:
		<script type="text/javascript" src="/openwebglobe/external/closure-library/closure/goog/base.js"></script>
		<script type="text/javascript" src="/openwebglobe/compiled/deps.js"></script>
		<script type="text/javascript">goog.require('owg.OpenWebGlobe');</script>
%else:
		<script type="text/javascript" src="/openwebglobe/compiled/owg-optimized.js"></script>
%end
		<title>TileCloud</title>
	</head>
	<body>
		<div style="width: 100%; height: 100%;">
			<canvas id="canvas">
			</canvas>
		</div>
		<script type="text/javascript">
			ogSetArtworkDirectory('/openwebglobe/art/');
			var context = ogCreateContextFromCanvas('canvas', true);
			var globe = ogCreateGlobe(context);
%for index, name in enumerate(names):
			ogAddImageLayer(globe, {
				url: ['/data/image'],
				layer: '{{index}}',
				service: 'owg'
			});
%end
		</script>
	</body>
</html>
