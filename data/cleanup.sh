#!/bin/bash

DIR="./shn-ground-truth"

deleted_count=0

for tif_file in "$DIR"/*.tif; do
    [ -e "$tif_file" ] || continue

    base_name="${tif_file%.tif}"

    # no .gt.txt file then delete image and box files.
    if [ ! -f "$base_name.gt.txt" ]; then
        echo "Deleting $tif_file (no matching .gt.txt found)"
        rm -f "$tif_file"
        echo "Deleting $base_name.box (no matching .gt.txt found)"
        rm -f "$base_name.box"

        ((deleted_count++))
    fi

    # no .box file then delete image and .gt.txt files.
    if [ ! -f "$base_name.box" ]; then
        echo "Deleting $base_name.gt.txt (no matching .box found)"
        rm -f "$base_name.gt.txt"
        echo "Deleting $tif_file (no matching .box found)"
        rm -f "$tif_file"
    fi
done

if [ "$deleted_count" -eq 0 ]; then
    echo "No files needed to be deleted - all .tif files have matching .gt.txt files"
else
    echo "Total files deleted: $deleted_count"
fi