from normalization_utils import split_by_delimiters
from abbreviation_mapper import map_morph_to_abbreviation, map_pos_to_abbreviation
import re

# Function to extract the main word, transcription, part of speech, and variant
def extract_main_word_and_pos(result_div, unmatched_abbreviations, session_id):
    word_section = result_div.find('h5', class_='titreamz')
    word_tifinagh = word_section.find('b').text  # The main word
    word_transcription = word_section.find('i').text.strip("[]")  # Remove brackets
    
    remaining_text = word_section.get_text().replace(word_tifinagh, "").replace(f"[{word_transcription}]", "").strip()
    tifinagh_pattern = re.compile(r"[ⴰ-⵿]")
    match = tifinagh_pattern.search(remaining_text)
    
    if match:
        tifinagh_start_index = match.start()
        pos_tag = remaining_text[:tifinagh_start_index].strip()
        variant_text = remaining_text[tifinagh_start_index:].strip()
        variant_cleaned = split_by_delimiters(variant_text)
    else:
        pos_tag = remaining_text
        variant_cleaned = []
    
    pos_tag_cleaned = pos_tag.strip().split(" et ")
    pos_tag_abbreviated = map_pos_to_abbreviation(pos_tag_cleaned, unmatched_abbreviations, session_id)
    
    return word_tifinagh, word_transcription, pos_tag_abbreviated, variant_cleaned

# Function to extract morphology data
def extract_morphology(result_div, unmatched_abbreviations, session_id):
    morphology = []
    ul_elements = result_div.find_all('ul', class_='titreamz')
    if len(ul_elements) > 0:
        form_list = ul_elements[0].find_all('li')
        for form in form_list:
            form_text = form.text.split(':')
            if len(form_text) == 2:
                key = form_text[0].strip()
                value = form.find('b').text.strip()
                key_abbreviated = map_morph_to_abbreviation(key, unmatched_abbreviations, session_id)
                value_cleaned = split_by_delimiters(value)
                morphology.append({key_abbreviated: value_cleaned})
    return morphology

# Function to extract senses
def extract_senses(result_div):
    senses = []
    ul_elements = result_div.find_all('ul')  # Find all 'ul' tags
    
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
def extract_related_phrases(result_div):
    related_phrases = []
    
    # We assume the third <ul> (or one with specific characteristics) contains the related phrases
    ul_elements = result_div.find_all('ul')  # Find all 'ul' tags

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
