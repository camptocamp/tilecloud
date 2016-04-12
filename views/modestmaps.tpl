<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
        <script type="text/javascript" src="https://raw.github.com/stamen/modestmaps-js/master/modestmaps.min.js"></script>
        <style type="text/css">
            html, body, #map {
                margin: 0;
                padding: 0;
                height: 100%;
            }
        </style>
        <title>Modest Maps - TileCloud</title>
    </head>
    <body>
        <div id="map" class="map" style="width: 100%; height: 100%;">
        </div>
        <script type="text/javascript">
            var layers = [];
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
            layers.push(new MM.Layer(new MM.TemplatedMapProvider('/tiles/{{index}}/tiles/{Z}/{X}/{Y}')));
%end
%end
            var map = new MM.Map('map', layers);
        </script>
    </body>
</html>
