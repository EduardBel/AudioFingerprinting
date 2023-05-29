#!/bin/bash

# Variables to store scores
correct_count=0
incorrect_count=0

# Function to process a single file
process_file() {
    filename=$(basename "$1")
    
    # Run the identify.py script and capture the exit code
    python3 identify.py -d songs.db -i "$1" > /dev/null 2>&1
    exit_code=$?
    
    # Check the exit code and update the scores
    if [ $exit_code -eq 0 ]; then
        ((correct_count++))
    else
        echo "Incorrect file identification: $filename"
        ((incorrect_count++))
    fi
}

# Find all .wav files in the samples directory and its subfolders
echo "\nProcessing clean_samples files..."
files=$(find samples/clean_samples -type f -name "*.wav")
while IFS= read -r file; do
    process_file "$file"
done <<< "$files"
clean_correct_count=$correct_count
clean_incorrect_count=$incorrect_count

correct_count=0
incorrect_count=0

echo "\nProcessing filtered_samples files..."
files=$(find samples/filtered_samples -type f -name "*.wav")
while IFS= read -r file; do
    process_file "$file"
done <<< "$files"
clean_filtered_correct_count=$correct_count
clean_filtered_incorrect_count=$incorrect_count

correct_count=0
incorrect_count=0

echo "\nProcessing noisy_filtered_samples files..."
files=$(find samples/noisy_filtered_samples -type f -name "*.wav")
while IFS= read -r file; do
    process_file "$file"
done <<< "$files"
noisy_filtered_correct_count=$correct_count
noisy_filtered_incorrect_count=$incorrect_count

correct_count=0
incorrect_count=0

echo "\nProcessing noisy_samples files..."
files=$(find samples/noisy_samples -type f -name "*.wav")
while IFS= read -r file; do
    process_file "$file"
done <<< "$files"
noisy_correct_count=$correct_count
noisy_incorrect_count=$incorrect_count

# Print the scores
echo "Clean samples: $clean_correct_count correct, $clean_incorrect_count incorrect"
echo "Filtered samples: $clean_filtered_correct_count correct, $clean_filtered_incorrect_count incorrect"
echo "Noisy filtered samples: $noisy_filtered_correct_count correct, $noisy_filtered_incorrect_count incorrect"
echo "Noisy samples: $noisy_correct_count correct, $noisy_incorrect_count incorrect"
echo "Total correct runs: $((clean_correct_count + clean_filtered_correct_count + noisy_filtered_correct_count + noisy_correct_count))"
echo "Total incorrect runs: $((clean_incorrect_count + clean_filtered_incorrect_count + noisy_filtered_incorrect_count + noisy_incorrect_count))"
