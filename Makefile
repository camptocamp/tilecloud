# FIXME this still builds too much

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

.PHONY: pyflakes
pyflakes:
	find tilecloud -name \*.py | xargs pyflakes
	pyflakes tc-*

.PHONY: submodules
submodules: \
	boto \
	bottle.py

boto: submodules/boto
	ln -fs $</boto $@

submodules/boto: .gitmodules
	git submodule update submodules/boto

bottle.py: submodules/bottle
	ln -fs $</bottle.py $@

submodules/bottle: .gitmodules
	git submodule update submodules/bottle
