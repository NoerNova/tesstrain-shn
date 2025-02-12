#!/bin/bash

# Set the directory containing the files to convert
data_dir="$HOME/Labs/tesstrain/data/shn-ground-truth"

# Loop through all files in the directory
find "$data_dir" -type f -name "*.gt.txt" -print0 | while IFS= read -r -d $'\0' file; do
  # Determine the current encoding of the file (optional but recommended)
  # This helps avoid double-encoding and provides information about the original encoding
  file_encoding=$(file -bi "$file" | cut -d ';' -f 1)
  echo "Processing file: $file (Current encoding: $file_encoding)"


  # Convert the file to UTF-8 using iconv
  # -c:  Discard invalid characters instead of reporting an error
  # -o: Specify the output file. We'll use a temporary file.
  temp_file=$(mktemp)
  iconv -f "$file_encoding" -t UTF-8 -c "$file" > "$temp_file"

  # Overwrite the original file with the UTF-8 version
  mv "$temp_file" "$file"

  echo "File '$file' converted to UTF-8."

done

echo "Conversion complete."