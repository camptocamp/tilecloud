all: submodules example-data

example-data: \
	mapbox.haiti-terrain-grey.mbtiles \
	mapbox.control-room.mbtiles \
	mapbox.geography-class.mbtiles \
	mapbox.world-bank-borders-en.mbtiles

mapbox.control-room.mbtiles:
	curl http://a.tiles.mapbox.com/v3/$@ > $@

mapbox.haiti-terrain-grey.mbtiles:
	curl http://a.tiles.mapbox.com/v3/$@ > $@

mapbox.geography-class.mbtiles:
	curl http://a.tiles.mapbox.com/v3/$@ > $@

mapbox.world-bank-borders-en.mbtiles:
	curl http://a.tiles.mapbox.com/v3/$@ > $@

.PHONY: submodules
submodules: \
	submodules/WebViewer/compiled/owg-optimized.js \
	submodules/boto/boto \
	submodules/bottle/bottle.py \
	submodules/openlayers/build/OpenLayers.js

submodules/WebViewer/compiled/owg-optimized.js: submodules/WebViewer
	( cd submodules/WebViewer/scripts && make )

submodules/WebViewer: git-submodule-init .gitmodules
	git submodule update submodules/WebViewer

submodules/boto/boto: git-submodule-init .gitmodules
	git submodule update submodules/boto

submodules/bottle/bottle.py: git-submodule-init .gitmodules
	git submodule update submodules/bottle

submodules/openlayers/build/OpenLayers.js: submodules/openlayers
	( cd submodules/openlayers/build && ./build.py )

submodules/openlayers: git-submodule-init .gitmodules
	git submodule update submodules/openlayers

.PHONY: git-submodule-init
git-submodule-init:
	git submodule init
