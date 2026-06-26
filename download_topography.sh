#!/bin/bash

# Configuration
RESOLUTION="15s"
BASE_URL="https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s"
SUB_DIR="15s_surface_elev_gtif"
PROLOG_KB="etopo_global.pl"
MAX_JOBS=4 

cleanup() {
    echo -e "\nStopping and cleaning up..."
    kill $(jobs -p) 2>/dev/null
    exit
}
trap cleanup SIGINT

# Generate list of all tiles
tiles=()
for lat in N00 N15 N30 N45 N60 N75 N90 S15 S30 S45 S60 S75 S90; do
    for lon in E000 E015 E030 E045 E060 E075 E090 E105 E120 E135 E150 E165 W015 W030 W045 W060 W075 W090 W105 W120 W135 W150 W165 W180; do
        tiles+=("${lat}${lon}")
    done
done

# Worker function
process_tile() {
    local TILE=$1
    local TILE_FILENAME="ETOPO_2022_v1_${RESOLUTION}_${TILE}_surface.tif"
    local OUT_KB="kb_${TILE}.pl"
    
    echo "[STARTED]  Tile ${TILE}"
    
    if [ ! -f "$TILE_FILENAME" ] || ! gdalinfo "$TILE_FILENAME" >/dev/null 2>&1; then
        curl -fSL "${BASE_URL}/${SUB_DIR}/${TILE_FILENAME}" -o "$TILE_FILENAME"
    fi
    
    # Process if valid
    if gdalinfo "$TILE_FILENAME" >/dev/null 2>&1; then
        gdal_translate -of XYZ "$TILE_FILENAME" "tmp_${TILE}.xyz" >/dev/null 2>&1
        awk '{ if ($3 != "nan" && $3 > -32000) printf("z(%.5f, %.5f, %.2f).\n", $2, $1, $3); }' "tmp_${TILE}.xyz" > "$OUT_KB"
        rm -f "tmp_${TILE}.xyz"
        echo "[FINISHED] Tile ${TILE}"
    else
        echo "[ERROR]    Tile ${TILE} could not be processed."
    fi
    rm -f "$TILE_FILENAME"
}

# multiprocessing Loop
echo "Starting parallel processing of ${#tiles[@]} tiles with $MAX_JOBS concurrent jobs..."
for TILE in "${tiles[@]}"; do
    while [ $(jobs -r | wc -l) -ge $MAX_JOBS ]; do
        sleep 2
    done
    process_tile "$TILE" &
done

wait
echo "Consolidating results into ${PROLOG_KB}..."
echo ":- dynamic(z/3)." > "$PROLOG_KB"
cat kb_*.pl >> "$PROLOG_KB"
rm kb_*.pl

echo "Successfully built complete global KB: $PROLOG_KB"

# split into latitude based chunks
mkdir -p chunks
awk -F'[(),]' '{ lat = int($2); filename = sprintf("chunks/lat_%d.pl", lat); print $0 > filename }' etopo_global.pl
