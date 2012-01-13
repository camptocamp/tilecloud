all: example-data

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

.PHONY: pep8
pep8:
	find tilecloud tiles bin -name \*.py | xargs pep8.py
	pep8.py tc-*

.PHONY: pyflakes
pyflakes:
	find tilecloud tiles bin -name \*.py | xargs pyflakes
	pyflakes tc-*
