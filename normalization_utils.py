import unicodedata
import re

# Delimiters for splitting text
DELIMITERS = [',', '/', ';', '،', '؛']

# Normalize text to remove accents and make it lowercase
def normalize_text(text):
    text = unicodedata.normalize('NFD', text)
    text = ''.join([c for c in text if unicodedata.category(c) != 'Mn'])  # Remove accents
    return text.lower().strip()  # Ensure no leading/trailing spaces

# Function to split by the custom delimiters
def split_by_delimiters(text):
    return [part.strip() for part in re.split(r'[{},/،؛]+'.format("|".join(map(re.escape, DELIMITERS))), text) if part.strip()]
