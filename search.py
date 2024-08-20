import os
import sys
import time
from utils import format_time

DATA_DIRECTORY = "data-ref"
SEARCH_DIRECTORIES = ['ssn', 'ssn2']

def prompt_for_input():
    lastname = input("Enter lastname: ").strip().lower()
    firstname = input("Enter firstname: ").strip().lower()
    middle = input("Enter middle initial (optional): ").strip().lower()
    states_input = input("Enter state abbreviations separated by commas (optional): ").strip().lower()
    censor_ssn = input("Censor SSN in output? (y/n, default is y): ").strip().lower()

    states = [state.strip() for state in states_input.split(",")] if states_input else []
    censor_ssn = censor_ssn != 'n'

    return lastname, firstname, middle, states, censor_ssn

def search_files(lastname, firstname):
    results = {}
    for subdir in SEARCH_DIRECTORIES:
        lastname_file = os.path.join(DATA_DIRECTORY, subdir, lastname)
        if os.path.exists(lastname_file):
            with open(lastname_file, 'r') as file:
                for line in file:
                    fname, start_offset, end_offset = line.strip().split(',')
                    if fname == firstname:
                        if subdir not in results:
                            results[subdir] = []
                        results[subdir].append((int(start_offset), int(end_offset)))
    
    return results

def filter_and_censor(records, headers, middle, states, censor_ssn):
    matched_records = []
    for record in records:
        data = dict(zip(headers, record.split(',')))
        if middle and not data.get('middlename').lower().strip().startswith(middle):
            continue

        if states and data.get('st').lower().strip() not in states:
            continue

        if censor_ssn and 'ssn' in data:
            data['ssn'] = data['ssn'][:3] + 'x' * (len(data['ssn']) - 3)

        matched_records.append(data)
    
    return matched_records

def display_results(results):
    count = 0
    for result in results:
        for key, value in result.items():
            print(f"{key}={value}")
        print("-" * 20)
    print(" ")
    print(f"Total results: {len(results)}")

def main():
    lastname, firstname, middle,states, censor_ssn = prompt_for_input()
    
    start_time = time.time()
    
    offsets = search_files(lastname, firstname)
    if not offsets:
        print("No matching records found.")
        return

    # Assume each subdir in data-ref has a corresponding .txt file in the current directory
    records = []

    for subdir in offsets:
        csv_filename = os.path.basename(subdir) + ".txt"

        if not os.path.exists(csv_filename):
            print(f"Error: Matching CSV file '{csv_filename}' not found for directory '{subdir}'.")
            return

        with open(csv_filename, 'r') as file:    
            for start_offset, end_offset in offsets[subdir]:
                file.seek(start_offset)
                line = file.read(end_offset - start_offset).strip()
                records.append(line)

    # Read the header from the first matching CSV file
    with open(os.path.join(os.getcwd(), csv_filename), 'r') as file:
        headers = file.readline().strip().lower().split(',')

    results = filter_and_censor(records, headers, middle, states, censor_ssn)
    
    if results:
        display_results(results)
    else:
        print("No matching records found.")

    elapsed_time = time.time() - start_time
    print("  ")
    print(f"Search time: {format_time(elapsed_time)}")
    print(" ")
if __name__ == "__main__":
    main()
