#!/bin/bash

DIR="./shn-ground-truth"

deleted_count=0

for tif_file in "$DIR"/*.tif; do
    [ -e "$tif_file" ] || continue

    base_name="${tif_file%.tif}"

    if [ ! -f "$base_name.gt.txt" ]; then
        echo "Deleting $tif_file (no matching .gt.txt found)"
        rm -f "$tif_file"

        ((deleted_count++))
    fi
done

if [ "$deleted_count" -eq 0 ]; then
    echo "No files needed to be deleted - all .tif files have matching .gt.txt files"
else
    echo "Total files deleted: $deleted_count"
fi