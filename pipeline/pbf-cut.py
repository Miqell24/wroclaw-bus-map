#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Cuts data/osm/wroclaw.json (roads) and data/osm/wroclaw-rail.json (tram
track) out of the Geofabrik dolnoslaskie extract — the same JSON shape Overpass returns
('elements': ways with tags, node ids and geometry), so build.mjs cannot tell
the difference.

The sheet is the agglomeration: the city and the zone lines the county
carriers run out to Trzebnica, Olesnica, Olawa, Sroda Slaska and Sobotka.
"""
import json, os, re, sys
import osmium

ROOT = os.path.join(os.path.dirname(__file__), '..')
PBF = os.path.join(ROOT, 'data', 'dolnoslaskie-latest.osm.pbf')
ROAD_BOX = (50.92, 16.60, 51.30, 17.40)   # S, W, N, E — the whole agglomeration
RAIL_BOX = (51.02, 16.85, 51.20, 17.20)   # the tram network is the city
HW = re.compile(r'^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|busway|construction|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$')
RAIL = re.compile(r'^(tram|light_rail|construction)$')

road_file = os.path.join(ROOT, 'data/osm/wroclaw.json')
rail_file = os.path.join(ROOT, 'data/osm/wroclaw-rail.json')
need_road, need_rail = not os.path.exists(road_file), not os.path.exists(rail_file)
print('drogi:', need_road, '| szyny:', need_rail, flush=True)
if not need_road and not need_rail:
    sys.exit(0)
if not os.path.exists(PBF):
    sys.exit(f'brak {PBF} — pobierz go (pipeline/download.sh)')
os.makedirs(os.path.join(ROOT, 'data/osm'), exist_ok=True)
out_road, out_rail = [], []


class H(osmium.SimpleHandler):
    def way(self, w):
        tags = w.tags
        hw, rw = tags.get('highway'), tags.get('railway')
        is_road = need_road and hw is not None and HW.match(hw)
        is_rail = need_rail and rw is not None and RAIL.match(rw)
        if not is_road and not is_rail:
            return
        geom, ids = [], []
        la0, la1, lo0, lo1 = 90.0, -90.0, 180.0, -180.0
        for n in w.nodes:
            try:
                lo, la = n.lon, n.lat
            except osmium.InvalidLocationError:
                continue
            # node ids ride along: buildGraph() builds topology from el.nodes
            # and SILENTLY skips ways without them (the London t13 hole)
            ids.append(n.ref)
            geom.append({'lat': la, 'lon': lo})
            if la < la0: la0 = la
            if la > la1: la1 = la
            if lo < lo0: lo0 = lo
            if lo > lo1: lo1 = lo
        if len(geom) < 2:
            return
        el = {'type': 'way', 'id': w.id, 'nodes': ids, 'tags': {t.k: t.v for t in tags}, 'geometry': geom}
        if is_road and la1 >= ROAD_BOX[0] and la0 <= ROAD_BOX[2] and lo1 >= ROAD_BOX[1] and lo0 <= ROAD_BOX[3]:
            out_road.append(el)
        if is_rail and la1 >= RAIL_BOX[0] and la0 <= RAIL_BOX[2] and lo1 >= RAIL_BOX[1] and lo0 <= RAIL_BOX[3]:
            out_rail.append(el)


print('czytam', os.path.basename(PBF), flush=True)
H().apply_file(PBF, locations=True, idx='flex_mem')
GEN = 'pbf-cut.py (Geofabrik dolnoslaskie)'
if need_road:
    json.dump({'version': 0.6, 'generator': GEN, 'elements': out_road}, open(road_file, 'w'))
    print(f'drogi: {len(out_road)}', flush=True)
if need_rail:
    json.dump({'version': 0.6, 'generator': GEN, 'elements': out_rail}, open(rail_file, 'w'))
    print(f'torowiska: {len(out_rail)}', flush=True)
print('gotowe', flush=True)
