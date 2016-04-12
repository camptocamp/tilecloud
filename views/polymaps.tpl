<!doctype html>
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <meta name="viewport" content="initial-scale=1.0, user-scalable=no">
        <script type="text/javascript" src="https://raw.github.com/simplegeo/polymaps/master/polymaps.min.js"></script>
        <style type="text/css">
            html, body, #map {
                margin: 0;
                padding: 0;
                height: 100%;
            }
        </style>
        <title>Polymaps - TileCloud</title>
    </head>
    <body>
        <script type="text/javascript">
            var po = org.polymaps;
            var map = po.map()
                .container(document.body.appendChild(po.svg('svg')))
%for index, (name, tilestore) in enumerate(tilestores):
%if tilestore.content_type is None or tilestore.content_type.startswith('image/'):
                .add(po.image().url('/tiles/{{index}}/tiles/{Z}/{X}/{Y}'))
%end
%end
                .add(po.interact());
        </script>
    </body>
</html>
