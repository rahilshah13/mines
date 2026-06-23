#!/bin/bash

RESOLUTION="15s"
BASE_URL="https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO2022/data/15s"
SUB_DIR="15s_surface_elev_gtif"
PROLOG_KB="etopo_global.pl"

# Initialize Prolog KB
echo ":- dynamic(z/3)." > "$PROLOG_KB"
echo "% Format: z(Latitude, Longitude, ElevationInMeters)." >> "$PROLOG_KB"

for lat in N00 N15 N30 N45 N60 N75 N90 S15 S30 S45 S60 S75 S90; do
    for lon in E000 E015 E030 E045 E060 E075 E090 E105 E120 E135 E150 E165 W015 W030 W045 W060 W075 W090 W105 W120 W135 W150 W165 W180; do
        TILE="${lat}${lon}"
        TILE_FILENAME="ETOPO_2022_v1_${RESOLUTION}_${TILE}_surface.tif"
        DOWNLOAD_URL="${BASE_URL}/${SUB_DIR}/${TILE_FILENAME}"
        echo "Processing Tile: ${TILE}..."        
        curl -fSL "$DOWNLOAD_URL" -o "$TILE_FILENAME" || { echo "Skipping ${TILE}..."; continue; }        
        gdal_translate -of XYZ "$TILE_FILENAME" "tmp_${TILE}.xyz"        
        # Extract to Prolog format using 'z/3'
        awk '{
            if ($3 != "nan" && $3 > -32000) {
                printf("z(%.5f, %.5f, %.2f).\n", $2, $1, $3);
            }
        }' "tmp_${TILE}.xyz" >> "$PROLOG_KB"        
        rm "$TILE_FILENAME" "tmp_${TILE}.xyz"
    done
done

echo "Successfully built complete global KB: $PROLOG_KB"