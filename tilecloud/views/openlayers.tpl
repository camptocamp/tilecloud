<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no">

        <link
          rel="stylesheet"
          href="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/css/ol.css"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        >
        <link
          rel="stylesheet"
          href="https://unpkg.com/ol-layerswitcher@3.8.3/dist/ol-layerswitcher.css"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        />
        <script
          type="text/javascript"
          src="https://cdn.jsdelivr.net/gh/openlayers/openlayers.github.io@master/en/v6.9.0/build/ol.js"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        ></script>
        <script
          type="text/javascript"
          src="https://unpkg.com/ol-layerswitcher@3.8.3"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"
        ></script>
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
            var layers = [];
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
            layers.push(new ol.layer.Tile({
                source: new ol.source.XYZ({
                    url: '/tiles/{{index}}/tiles/{z}/{x}/{y}',
                }),
                title: '{{name}}',
%if getattr(tilestore, 'attribution', None):
                attribution: '{{!tilestore.attribution}}',
%end
            }));
%end
%end
            var map = new ol.Map({
                target: "map",
                layers: layers,
                view: new ol.View({
                    center: [0, 0],
                    zoom: 2,
%if resolutions:
                    resolutions: [{{resolutions}}],
%end
                }),
            });
%if len(tilestores) > 1:
            map.addControl(new ol.control.LayerSwitcher({
              activationMode: 'click',
              startActive: true
            }));
%end
        </script>
    </body>
</html>
