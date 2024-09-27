from fetch_html import fetch_html, failed_sessions
from data_extractors import extract_main_word_and_pos, extract_morphology, extract_senses, extract_related_phrases
from colorama import Fore, init
import json
import os
import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Initialize colorama for Windows
init(autoreset=True)

# List of session_ids to process (range from 10000 to 100000)
session_ids = [str(i) for i in range(143752, 144752)]

# Get the current date and time
current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

# Create logs folder with date information
log_folder = f"logs/{current_time}"
os.makedirs(log_folder, exist_ok=True)

# Define a function to process a single session ID
def process_session(session_id, unmatched_abbreviations):
    print(Fore.CYAN + f"Processing session_id: {session_id}")
    result_div = fetch_html(session_id)
    
    if result_div:
        try:
            # Step 1: Extract main word, transcription, POS, and variant
            word_tifinagh, word_transcription, pos_tag, variants = extract_main_word_and_pos(result_div, unmatched_abbreviations, session_id)
            morphology = extract_morphology(result_div, unmatched_abbreviations, session_id)
            senses = extract_senses(result_div)
            related_phrases = extract_related_phrases(result_div)
            
            # Save the extracted data for this session
            return {
                session_id: {
                    "mw": word_tifinagh,
                    "tr": word_transcription,
                    "pos": pos_tag,
                    "var": variants,
                    "morph": morphology,
                    "sens": senses,
                    "rp": related_phrases
                }
            }
        except Exception as e:
            print(Fore.RED + f"Error processing session_id {session_id}: {e}")
            return None
    else:
        return None

# Function to save data to a file
def save_data_to_file(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Parallelize execution using ThreadPoolExecutor
def fetch_sessions_parallel(session_ids, unmatched_abbreviations):
    results = []
    with ThreadPoolExecutor() as executor:
        # Submit tasks for each session_id
        future_to_session = {executor.submit(process_session, session_id, unmatched_abbreviations): session_id for session_id in session_ids}
        
        for future in as_completed(future_to_session):
            session_id = future_to_session[future]
            try:
                session_data = future.result()
                if session_data:
                    results.append(session_data)  # Add the processed data to the results
            except Exception as exc:
                print(Fore.RED + f"Session {session_id} generated an exception: {exc}")
    
    return results

# Function to split the session IDs into chunks of 1000
def chunk_session_ids(session_ids, chunk_size=1000):
    for i in range(0, len(session_ids), chunk_size):
        yield session_ids[i:i + chunk_size]

# Main execution
if __name__ == "__main__":
    # Split session_ids into chunks of 1000
    for session_chunk in chunk_session_ids(session_ids):
        session_start = session_chunk[0]
        session_end = session_chunk[-1]

        # Create a subfolder for each chunk
        chunk_folder = f"{log_folder}/{session_start}-{session_end}"
        os.makedirs(chunk_folder, exist_ok=True)

        # Dictionary to store data for the current chunk
        data = {}
        
        # New list for unmatched abbreviations for this chunk
        unmatched_abbreviations = []

        # Start parallel fetching for the current chunk
        session_results = fetch_sessions_parallel(session_chunk, unmatched_abbreviations)

        # Merge the results into the data dictionary
        for result in session_results:
            data.update(result)

        # Print separator for each session
        print(Fore.CYAN + "\n" + "=" * 50 + "\n")

        # Step 5: Save the collected data to a JSON file inside the chunk folder
        output_file = f'{chunk_folder}/extracted_data_{session_start}-{session_end}.json'
        save_data_to_file(data, output_file)
        print(Fore.GREEN + f"Data successfully saved to {output_file}")

        # Step 6: Save unmatched abbreviations to a log file inside the chunk folder
        if unmatched_abbreviations:
            output_file_warnings = f'{chunk_folder}/abbreviations_not_found_{session_start}-{session_end}.log'
            with open(output_file_warnings, 'w', encoding='utf-8') as f:  # 'w' to create new for each chunk
                for warning in unmatched_abbreviations:
                    f.write(warning + '\n')

            print(Fore.GREEN + f"Unmatched abbreviations saved to {output_file_warnings}")
        else:
            print(Fore.GREEN + "No unmatched abbreviations found.")

        # Step 7: After processing all sessions in the chunk, save failed session retrievals to a file inside the chunk folder
        if failed_sessions:
            output_file_failures = f'{chunk_folder}/failed_sessions_{session_start}-{session_end}.log'
            with open(output_file_failures, 'w', encoding='utf-8') as f:
                for failure in failed_sessions:
                    f.write(failure + '\n')

            print(Fore.GREEN + f"Failed session retrievals saved to {output_file_failures}")
        else:
            print(Fore.GREEN + "No failed session retrievals found.")
