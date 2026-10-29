# geocoder-site

The site at https://geocoder.syalia.com: one static page about Geocoder, offline
geocoding for Cuba on OpenStreetMap data.

- `site/` is what GitHub Pages publishes. `site/index.html` is generated; edit
  `template.html` and rebuild.
- `scripts/extract.py` pulls the streets of a small area of Vedado out of the
  Cuba extract from Geofabrik (`cuba-latest.osm.pbf`) with pyosmium.
- `scripts/build_svg.py` turns them into the SVG map and the example results the
  page shows. The examples are illustrations computed from OpenStreetMap
  geometry for this page, not output of the Geocoder service.
- `scripts/build_page.py` fills `template.html` with them and writes
  `site/index.html`.

```bash
python3 scripts/extract.py cuba-latest.osm.pbf vedado.json   # needs pyosmium
python3 scripts/build_svg.py                                  # vedado.json -> mock.json
python3 scripts/build_page.py                                 # mock.json -> site/index.html
python3 -m http.server -d site 8000
```

Fonts (Archivo, Inter, IBM Plex Mono) are served from `site/fonts/` under the
SIL Open Font License. Map data © OpenStreetMap contributors, ODbL.
