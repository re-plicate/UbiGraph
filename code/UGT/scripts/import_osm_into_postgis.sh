#!/bin/bash
export OSM_CREATE='osm2pgsql -k -c -d sfpark -U postgres -H localhost -W -S 'D:/tools/PostgreSQL/osm2pgsql-bin/default.style''

# extract from OSM file
$OSM_CREATE osm/osm_sfpark_blocks.osm