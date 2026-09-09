#!/usr/bin/env bash
# Downloads input data: the GTFS feed, the OSM networks (Geofabrik + pyosmium)
# and MapLibre GL. Everything is cached — re-running only fetches what is
# missing.
#
# Wrocław: ONE feed carries the whole agglomeration. The city publishes it as
# open data (UM Wrocław; the copy this script takes is odt.org.pl's mirror,
# which is the same file kept current — the dane.gov.pl resource of the same
# name is a 2016 snapshot and must NOT be used). In it ride MPK's trams and
# city buses and the suburban and zone lines of the county carriers — DLA
# Wrocław, PT KŁOSOK and NOWAK TRANSPORT — split at build time by route_type
# (3 = bus, 0 = tram). The feed ships shapes, direction_id and its own line
# classification (route_types.txt: normal / express / suburban / zone / night).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p data/gtfs data/osm web/vendor

# 1) GTFS — the city's bundle
if [ ! -f data/gtfs/routes.txt ]; then
  echo "== GTFS Wrocław =="
  curl -fL --retry 3 --max-time 600 \
    -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36" \
    -o data/gtfs.zip "https://data.odt.org.pl/gtfs/wroclaw-gtfs.zip"
  unzip -o data/gtfs.zip -d data/gtfs
fi

# 2) OSM — from the Geofabrik dolnośląskie extract, not Overpass: every public
#    mirror answered 504 for an hour on 9.09.2026, and this frame (56 × 42 km
#    of roads) is exactly the kind of query they refuse. pipeline/pbf-cut.py
#    (needs `pip3 install --user osmium`) writes the same JSON Overpass would
#    have returned, node ids included: the road box over the agglomeration
#    (50.92–51.30 N, 16.60–17.40 E) and the tram box over the city
#    (51.02–51.20 N, 16.85–17.20 E).
if [ ! -f data/osm/wroclaw.json ] || [ ! -f data/osm/wroclaw-rail.json ]; then
  python3 -c "import osmium" 2>/dev/null || { echo "brak pakietu osmium — zainstaluj: pip3 install --user osmium" >&2; exit 1; }
  if [ ! -f data/dolnoslaskie-latest.osm.pbf ]; then
    echo "== Geofabrik dolnoslaskie-latest.osm.pbf =="
    curl -fL --retry 5 --retry-delay 5 -C - --max-time 3600 -o data/dolnoslaskie-latest.osm.pbf \
      "https://download.geofabrik.de/europe/poland/dolnoslaskie-latest.osm.pbf"
  fi
  echo "== cutting OSM out of the extract =="
  python3 pipeline/pbf-cut.py
fi

# 3) MapLibre GL (vendored, no CDN at runtime)
if [ ! -f web/vendor/maplibre-gl.js ]; then
  echo "== MapLibre GL =="
  curl -fL --retry 3 -o web/vendor/maplibre-gl.js  https://unpkg.com/maplibre-gl@5.6.1/dist/maplibre-gl.js
  curl -fL --retry 3 -o web/vendor/maplibre-gl.css https://unpkg.com/maplibre-gl@5.6.1/dist/maplibre-gl.css
fi

echo "OK — data ready:"
du -sh data/gtfs data/osm/wroclaw.json data/osm/wroclaw-rail.json 2>/dev/null || true
