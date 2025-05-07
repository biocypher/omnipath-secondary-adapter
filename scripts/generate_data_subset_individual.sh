#!/bin/bash

# Check if the input file is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <input_file.csv> <output_file.csv> <number of samples>"
    exit 1
fi

input_file="$1"
output_file="$2"
n_samples="$3"

# Get the header
head -n 1 "$input_file" > "$output_file"

# Shuffle and select 100 random rows (excluding the header)
#tail -n +2 "$input_file" | shuf | head -n 10000 >> "$output_file"

# Take the first rows
tail -n +2 "$input_file" | head -n $n_samples >> "$output_file"


echo "Random sample saved to $output_file"
