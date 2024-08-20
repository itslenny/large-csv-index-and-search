import os
import sys
import time
import re
from utils import format_time

DATA_DIRECTORY = "data-ref"
# cache 1GB in memory before writing to disk
CACHE_SIZE_LIMIT = 1 * 1024 * 1024 * 1024

def process_csv(csv_file):
    # Extract the file name without extension for directory naming
    csv_filename = os.path.splitext(os.path.basename(csv_file))[0]
    directory_path = os.path.join(DATA_DIRECTORY, csv_filename)

    # Create the directory if it doesn't exist
    os.makedirs(directory_path, exist_ok=True)

    # Get the total size of the file for progress calculation
    total_size = os.path.getsize(csv_file)

    # Initialize cache
    cache = {}
    current_cache_size = 0

    with open(csv_file, 'r', encoding='utf-8', errors='replace') as file:
        # Read the first line to map headers to column numbers
        header_line = file.readline().strip().lower()
        headers = header_line.split(',')

        # Map headers to column numbers
        header_map = {header: idx for idx, header in enumerate(headers)}

        lastname_col = header_map.get('lastname')
        firstname_col = header_map.get('firstname')

        if lastname_col is None or firstname_col is None:
            print("Error: CSV must contain 'lastname' and 'firstname' columns.")
            return

        # Initialize variables for progress tracking
        start_time = time.time()
        last_percent = -1
        current_position = file.tell()  # Start position after reading header

        print("Read headers successfully. Reading lines...")

        item_skip_count = 0

        # Go through the remaining lines in batches
        while True:
            lines = file.readlines(10000)  # Read 10,000 lines at a time
            if not lines:
                break

            for line in lines:
                line_len = len(line)
                line = line.strip()

                if not line:
                    # if the line is blank, skip it, but increment current_position
                    current_position += line_len + 1
                    continue

                line_data = line.split(',')
                lastname = line_data[lastname_col].strip().lower()
                firstname = line_data[firstname_col].strip().lower()

                if not lastname or not firstname:
                    # if no names, skip it, but increment current_position
                    current_position += line_len + 1
                    continue

                end_byte_offset = current_position + line_len
                entry = f"{firstname},{current_position},{end_byte_offset}\n"

                if lastname not in cache:
                    cache[lastname] = []
                cache[lastname].append(entry)
                current_cache_size += len(entry)

                # increment position counter
                current_position = end_byte_offset + 1

            # Check if cache size exceeds limit
            if current_cache_size >= CACHE_SIZE_LIMIT:
                flush_cache(cache, directory_path)
                cache.clear()
                current_cache_size = 0

            # Progress tracking (output only once per %)
            percent_complete = int((current_position / total_size) * 100)
            if percent_complete > 0 and percent_complete > last_percent:
                last_percent = percent_complete
                elapsed_time = time.time() - start_time
                estimated_total_time = elapsed_time / (percent_complete / 100)
                estimated_remaining_time = estimated_total_time - elapsed_time

                print(f"{percent_complete}% complete | Elapsed time: {format_time(elapsed_time)} | "
                      f"Estimated time remaining: {format_time(estimated_remaining_time)} | Cache size: {current_cache_size}")

        # Flush any remaining data in the cache at the end
        flush_cache(cache, directory_path)

def flush_cache(cache, directory_path):
    """Flush the in-memory cache to disk."""
    print(f"Flushing cache to disk. Item count: {sum(len(v) for v in cache.values())}")
    for lastname, entries in cache.items():
        lastname_file = os.path.join(directory_path, re.sub(r'[^a-zA-Z0-9]', '-', lastname))
        with open(lastname_file, 'a') as lname_file:
            lname_file.writelines(entries)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: No input file provided. Please specify a file.")
        sys.exit(1)

    csv_file = sys.argv[1]
    process_csv(csv_file)
