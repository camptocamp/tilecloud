<!doctype html>
<html>
        <head>
                <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
                <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
                <link rel="stylesheet" href="http://leaflet.cloudmade.com/dist/leaflet.css" type="text/css">
                <script type="text/javascript" src="http://leaflet.cloudmade.com/dist/leaflet.js"></script>
                <style type="text/css">
                        html, body, #map {
                                margin: 0;
                                padding: 0;
                                height: 100%;
                        }
                </style>
                <title>Leaflet - TileCloud</title>
        </head>
        <body>
                <div id="map" style="width: 100%; height: 100%;">
                </div>
                <script type="text/javascript">
                        var map = new L.Map('map');
                        var layer_names = {};
%for index, (name, tile_store) in enumerate(tile_stores):
%if tile_store.content_type is None or tile_store.content_type.startswith('image/'):
                        layer_names['{{name}}'] = new L.TileLayer('/data/image/{{index}}/tiles/{z}/{x}/{y}', {
%if getattr(tile_store, 'attribution', None):
                            attribution: '{{!tile_store.attribution}}'
%end
                        });
                        map.addLayer(layer_names['{{name}}']);
%end
%end
                        var layersControl = new L.Control.Layers({}, layer_names);
                        map.addControl(layersControl);
                        map.setView(new L.LatLng(0, 0), 0);
                </script>
        </body>
</html>
