#!/bin/bash

# Check if the directory is provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <input_directory> <output_directory>"
    exit 1
fi

input_dir="$1"
output_dir="$2"
extension="decomp"

# Create the output directory if it doesn't exist
mkdir -p "$output_dir"

# Loop through all CSV files in the input directory
for file in "$input_dir"/*."$extension"; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        output_file="$output_dir/subset_$filename"
        
        # Extract the header
        head -n 1 "$file" > "$output_file"
        
        # Shuffle and select 100 random rows (excluding the header)
        tail -n +2 "$file" | shuf | head -n 10000 >> "$output_file"

        echo "Processed: $filename -> $output_file"
    fi
done

echo "All CSV files have been processed. Subsets saved in $output_dir"
