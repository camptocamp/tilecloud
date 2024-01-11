<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
        <script type="text/javascript" src="http://maps.googleapis.com/maps/api/js?sensor=false"></script>
        <style type="text/css">
            html, body, #map {
                margin: 0;
                padding: 0;
                height: 100%;
            }
        </style>
        <title>Google Maps - TileCloud</title>
    </head>
    <body>
        <div id="map" style="width: 100%; height: 100%;">
        </div>
        <script type="text/javascript">
            var mapTypes = [], mapTypeIds = [];
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
            mapTypes.push(new google.maps.ImageMapType({
                alt: '{{index}}',
                getTileUrl: function(coord, zoom) {
                    return '/tiles/{{index}}/tiles/' + zoom + '/' + coord.x + '/' + coord.y;
                },
                name: '{{index}}',
                tileSize: new google.maps.Size(256, 256),
                maxZoom: 32
            }));
            mapTypeIds.push('{{index}}');
%end
%end
            var map = new google.maps.Map(document.getElementById('map'), {
                center: new google.maps.LatLng(0, 0),
                mapTypeControlOptions: {
                    mapTypeIds: mapTypeIds
                },
                mapTypeId: mapTypeIds[0],
                zoom: 0
            });
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
            map.mapTypes.set(mapTypeIds[{{index}}], mapTypes[{{index}}]);
%end
%end
        </script>
    </body>
</html>
