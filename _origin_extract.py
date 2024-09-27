from bs4 import BeautifulSoup
from colorama import Fore, init
import requests
import json
import re
import unicodedata

# Initialize colorama for Windows
init(autoreset=True)

# Delimiters for splitting text
DELIMITERS = [',', '/', ';', '،', '؛']

# Initialize a list to store failed session retrievals
failed_sessions = []

# Function to fetch HTML from a URL
def fetch_html(session_id):
    url = f"https://tal.ircam.ma/dglai/search/indexs?session={session_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.text  # Return the HTML content
    else:
        print(Fore.RED + f"Failed to retrieve HTML from {session_id}. Status code: {response.status_code}")
        failed_sessions.append(f"Failed to retrieve HTML from {session_id}. Status code: {response.status_code}")
        return None

# Normalize text to remove accents and make it lowercase
def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])  # Remove accents
    return text.lower().strip()  # Ensure no leading/trailing spaces

# Function to split by the custom delimiters
def split_by_delimiters(text):
    return [part.strip() for part in re.split(r'[{},/،؛]+'.format("|".join(map(re.escape, DELIMITERS))), text) if part.strip()]

# Morphology abbreviations
MORPH_ABBREVIATIONS = {
    "etat d'annexion": "annex",
    "pluriel etat libre": "pl_lib",
    "pluriel etat d'annexion": "pl_annex",
    "féminin etat libre": "fem_lib",
    "féminin etat d'annexion": "fem_annex",
    "féminin pluriel etat libre": "fem_pl_lib",
    "féminin pluriel etat d'annexion": "fem_pl_annex",
    "accompli": "accomp",
    "accompli négatif": "accomp_neg",
    "inaccompli": "inaccomp"
}

# Function to map a morphology label to its abbreviation
def map_morph_to_abbreviation(label):
    normalized_label = normalize_text(label)
    for full_label, abbrev in MORPH_ABBREVIATIONS.items():
        if normalize_text(full_label) == normalized_label:
            return abbrev
    # Warn if no match is found
    print(Fore.YELLOW + f"Warning: No abbreviation found for morphology label '{label}'")
    unmatched_abbreviations.append(f"Session ID: {session_id} - No abbreviation found for morphology label '{label}'")
    return label  # Keep original if no match

# Part of speech abbreviations
POS_ABBREVIATIONS = {
    "adjectif": "adj",
    "adverbe": "adv",
    "auxiliaire": "aux",
    "complément dʼobjet direct": "cod",
    "conjonction": "conj",
    "déictique": "deic",
    "démonstratif": "dém",
    "déterminant": "dét",
    "exclamatif": "excl",
    "féminin": "fém",
    "grammaire": "gram",
    "interjection": "interj",
    "interrogation": "interrog",
    "intransitif": "intr",
    "littéralement": "litt",
    "locution": "loc",
    "masculin": "masc",
    "nom": "n",
    "nom masculin": "nmasc",
    "nom féminin": "nfem",
    "nom collectif": "ncol",
    "néologisme": "néo",
    "onomatopée": "ono",
    "numéral": "num",
    "particule": "part",
    "participe": "pcp",
    "personne": "pers",
    "pluriel": "pl",
    "présentatif": "prés",
    "pronom": "pron",
    "singulier": "sing",
    "transitif": "tr",
    "verbe": "v",
    "variante": "var",
    "subordonnant": "sub"
}

# Function to map a part of speech to its abbreviation
def map_pos_to_abbreviation(pos_tags):
    abbreviations = []
    for tag in pos_tags:
        normalized_tag = normalize_text(tag)
        for full_pos, abbrev in POS_ABBREVIATIONS.items():
            normalized_full_pos = normalize_text(full_pos)
            if normalized_tag == normalized_full_pos:
                abbreviations.append(abbrev)
                break
        else:
            # Warn if no match is found
            print(Fore.YELLOW + f"Warning: No abbreviation found for part of speech '{tag}'")
            unmatched_abbreviations.append(f"Session ID: {session_id} - No abbreviation found for part of speech '{tag}'")
            abbreviations.append(tag)  # Keep original if no match
    return abbreviations

# Function to extract the main word, transcription, part of speech, and variant
def extract_main_word_and_pos(soup):
    word_section = soup.find('h5', class_='titreamz')
    
    # Extract Tifinagh main word and transcription
    word_tifinagh = word_section.find('b').text  # The main word
    word_transcription = word_section.find('i').text.strip("[]")  # Remove brackets from transcription
    
    # Get the remaining text after extracting the main word and transcription
    remaining_text = word_section.get_text().replace(word_tifinagh, "").replace(f"[{word_transcription}]", "").strip()
    
    # Use regex to detect the first Tifinagh character in the remaining text
    tifinagh_pattern = re.compile(r"[ⴰ-⵿]")
    match = tifinagh_pattern.search(remaining_text)
    
    if match:
        tifinagh_start_index = match.start()
        
        # Extract the Part of Speech (text before the first Tifinagh character)
        pos_tag = remaining_text[:tifinagh_start_index].strip()
        
        # Extract variants (text starting from the first Tifinagh character)
        variant_text = remaining_text[tifinagh_start_index:].strip()
        
        # Split the variant text using the delimiters
        variant_cleaned = split_by_delimiters(variant_text)
        
    else:
        # No Tifinagh characters found, all remaining text is Part of Speech
        pos_tag = remaining_text
        variant_cleaned = []
    
    # Join the part of speech into a list and split by "et" if necessary
    pos_tag_cleaned = pos_tag.strip().split(" et ")
    
    # Abbreviate the part of speech using the normalized version
    pos_tag_abbreviated = map_pos_to_abbreviation(pos_tag_cleaned)
    
    return word_tifinagh, word_transcription, pos_tag_abbreviated, variant_cleaned

# Function to extract morphology data
def extract_morphology(soup):
    morphology = []
    
    # Extract the first list (ul) and get all list items (li)
    ul_elements = soup.find_all('ul', class_='titreamz')
    if len(ul_elements) > 0:
        form_list = ul_elements[0].find_all('li')
        for form in form_list:
            form_text = form.text.split(':')  # Split by colon to get label and value
            if len(form_text) == 2:
                key = form_text[0].strip()
                value = form.find('b').text.strip()
                
                # Abbreviate the morphology label
                key_abbreviated = map_morph_to_abbreviation(key)
                
                # Split the value by delimiters if needed
                value_cleaned = split_by_delimiters(value)
                
                morphology.append({key_abbreviated: value_cleaned})
            else:
                print(Fore.RED + "Malformed morphology entry.")
    else:
        print(Fore.RED + "No morphology found.")
    
    return morphology

# Function to extract senses
def extract_senses(soup):
    senses = []
    ul_elements = soup.find_all('ul')  # Find all 'ul' tags
    
    for ul in ul_elements:
        sense_list = ul.find_all('li')  # Check each 'ul' for 'li' tags
        for li in sense_list:
            if 'Sens' in li.text:  # We are only interested in <li> that contains 'Sens'
                sense_text = list(li.stripped_strings)
                
                # Check if we have at least the French and Arabic parts
                if len(sense_text) >= 3:
                    # Clean up French senses
                    fr_senses = split_by_delimiters(sense_text[1].strip())
                    
                    # Clean up Arabic senses
                    ar_senses = split_by_delimiters(sense_text[2].strip())
                    
                    senses.append({"fr": fr_senses, "ar": ar_senses})
    
    if senses:
        return senses
    else:
        print("No senses found in the document.")
        return []

# Function to extract related phrases
def extract_related_phrases(soup):
    related_phrases = []
    
    # We assume the third <ul> (or one with specific characteristics) contains the related phrases
    ul_elements = soup.find_all('ul')  # Find all 'ul' tags

    # Iterate over the <ul> elements to find the correct one for related phrases
    for ul in ul_elements:
        if "titreamz" in ul.get("class", []):  # Ensure we are only considering specific classes for related phrases
            continue  # Skip lists related to morphology or other sections

        # Now look for <li> tags inside this <ul> to extract related phrases
        phrase_list = ul.find_all('li')
        for li in phrase_list:
            phrase = {}
            phrase_title = li.find('b')  # Find the <b> tag inside <li> which contains the Tifinagh phrase
            if phrase_title:
                phrase['zgh'] = phrase_title.text.strip()  # Tifinagh phrase
            else:
                continue  # Skip if no <b> tag found

            # Now find the French and Arabic translations
            translations = li.find_all('br')
            if len(translations) >= 2:  # Ensure there are at least two <br> elements for fr and ar
                phrase['fr'] = translations[0].next_sibling.strip()
                phrase['ar'] = translations[1].next_sibling.strip()

            # Append to related phrases if we have a valid phrase and its translations
            if 'fr' in phrase and 'ar' in phrase:
                related_phrases.append(phrase)

    if related_phrases:
        return related_phrases
    else:
        return []  # Return empty if no valid related phrases found

# List of session_ids to process
session_ids = ["134417", "147756", "142203", "142203", "136591", "138080", "135105", "132336"]  # Add your list of session_ids here

# Dictionary to store all extracted data
data = {}
# List to store unmatched abbreviations
unmatched_abbreviations = []  


# Loop through each session_id
for session_id in session_ids:
    print(Fore.CYAN + f"Processing session_id: {session_id}")
    
    # Fetch the HTML content for each session
    html = fetch_html(session_id)
    
    if html:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Step 1: Extract main word, transcription, POS, and variant
        word_tifinagh, word_transcription, pos_tag, variants = extract_main_word_and_pos(soup)
        
        # Step 2: Extract morphology data
        morphology = extract_morphology(soup)
        
        # Step 3: Extract senses
        senses = extract_senses(soup)
        
        # Step 4: Extract related phrases
        related_phrases = extract_related_phrases(soup)
        
        # Save all extracted data for this session in a dictionary
        data[session_id] = {
            "mw": word_tifinagh,
            "tr": word_transcription,
            "pos": pos_tag,
            "var": variants,
            "morph": morphology,
            "sens": senses,
            "rp": related_phrases
        }

        # Print separator for each session
        print(Fore.CYAN + "\n" + "="*50 + "\n")

# Step 5: Save the collected data to a JSON file
output_file = 'extracted_data.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

print(Fore.GREEN + f"Data successfully saved to {output_file}")

# Step 6: # After processing all sessions, save unmatched abbreviations to a file if there are any
if unmatched_abbreviations:
    output_file_warnings = 'abbreviations_not_found.txt'
    with open(output_file_warnings, 'w', encoding='utf-8') as f:
        for warning in unmatched_abbreviations:
            f.write(warning + '\n')

    print(Fore.GREEN + f"Unmatched abbreviations saved to {output_file_warnings}")
else:
    print(Fore.GREEN + "No unmatched abbreviations found.")

# Step 7: After processing all sessions, save failed session retrievals to a file if there are any
if failed_sessions:
    output_file_failures = 'failed_sessions.txt'
    with open(output_file_failures, 'w', encoding='utf-8') as f:
        for failure in failed_sessions:
            f.write(failure + '\n')

    print(Fore.GREEN + f"Failed session retrievals saved to {output_file_failures}")
else:
    print(Fore.GREEN + "No failed session retrievals found.")