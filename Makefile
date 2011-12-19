# FIXME this still builds too much

all: submodules example-data

.PHONY: clean
clean:
	find tilecloud tiles -name \*.pyc | xargs rm -f

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
	find tilecloud tiles bin -name \*.py | xargs pyflakes
	pyflakes tc-*

.PHONY: submodules
submodules: bottle.py

bottle.py: submodules/bottle
	ln -fs $</bottle.py $@

submodules/bottle: .gitmodules
	git submodule update submodules/bottle
	git submodule init
