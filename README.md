# Wrocław Public Transport — interactive map

Interactive, poster-grade map of the public transport of **Wrocław and its
agglomeration**: MPK's trams and city buses, and the suburban and zone lines
the county carriers run for the communes around — **138 lines / 4 397 km**
drawn along the real street and track geometry, weighted mean matching error
2.9 m.

## Live

**https://miqell24.github.io/wroclaw-bus-map/** — GitHub Pages from `main:/docs`. Local build on port 8186 (`npm run serve`).

One feed carries the whole sheet. The city publishes it as open data (UM
Wrocław); this pipeline takes odt.org.pl's mirror, which is the same file kept
current — **the dane.gov.pl resource of the same name is a 2016 snapshot and
must not be used**. In it ride six operators, and the feed classifies its own
lines (`route_types.txt`):

| what the feed calls it | lines |
|---|---|
| Normalna tramwajowa | 26 trams: 0–24 and the tourist line T |
| Normalna autobusowa | 56 city buses, 100–153 (plus 306, 310, 315, 319, 343, 345 and the 747 to the airport) |
| Pospieszna autobusowa | 4 express: A, D, K, N |
| Podmiejska autobusowa | 3 suburban: 602, 607, 612 |
| Strefowa autobusowa | 31 zone lines, 903–967 — **the agglomeration**, run by DLA Wrocław, PT KŁOSOK and NOWAK TRANSPORT |
| Nocna autobusowa | 17 night: 206 and 240–259 |
| Okresowa autobusowa | the seasonal 715 |

| mode | route_type | lines | graph |
|---|---|---|---|
| buses | 3 | 112 | OSM roadways |
| trams | 0 | 26 | `railway=tram` + `light_rail` |

Worth knowing:

- **No number is used twice on this sheet**, across all six operators and both
  modes, so no line needs the operator prefix this family gives to shared
  numbers elsewhere. Every chip prints exactly what the stop flag prints.
- **Night lines print black and sort last** (the family rule): here that is the
  2xx family, which the feed's own classification confirms.
- The sheet reaches as far as the timetable does: Trzebnica in the north,
  Oleśnica in the east, Oława and Siechnice in the south-east, Sobótka and Kąty
  Wrocławskie in the south-west — 56 × 42 km.
- **The OSM comes from Geofabrik, not Overpass**: on 9.09.2026 every public
  mirror answered the road query with 504, so `pipeline/pbf-cut.py` (needs
  `pip3 install --user osmium`) cuts the road and tram boxes out of
  `dolnoslaskie-latest.osm.pbf`.

## Two views

The panel's **Corridors / Lines** switch redraws the same data two ways.
*Corridors* is one stroke per roadway, the whole network in its mode colours
(navy buses, red trams). *Lines* draws every line on its own — up to four
coloured strands side by side, anything busier as one grey trunk with its
numbers beside it (`npm run lines`, checked by `npm run audit`).

## Pipeline

`npm run download` fetches the feed, cuts the OSM and vendors MapLibre GL.
`npm run build` map-matches every line (HMM/Viterbi on the OSM graphs) and
writes GeoJSON to `data/out/`; `npm run lines` adds the line-by-line view.
`npm run serve` hosts the map at http://localhost:8186.

Data: GTFS UM Wrocław (odt.org.pl mirror) · base map © OpenFreeMap /
OpenMapTiles / OpenStreetMap contributors.
