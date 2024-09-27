from colorama import Fore
from normalization_utils import normalize_text

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

# Function to map a morphology label to its abbreviation
def map_morph_to_abbreviation(label, unmatched_abbreviations, session_id):
    normalized_label = normalize_text(label)
    for full_label, abbrev in MORPH_ABBREVIATIONS.items():
        if normalize_text(full_label) == normalized_label:
            return abbrev
    print(Fore.YELLOW + f"Warning: No abbreviation found for morphology label '{label}'")
    unmatched_abbreviations.append(f"Session ID: {session_id} - No abbreviation found for morphology label '{label}'")
    return label  # Keep original if no match

# Function to map a part of speech to its abbreviation
def map_pos_to_abbreviation(pos_tags, unmatched_abbreviations, session_id):
    abbreviations = []
    for tag in pos_tags:
        normalized_tag = normalize_text(tag)
        for full_pos, abbrev in POS_ABBREVIATIONS.items():
            if normalize_text(full_pos) == normalized_tag:
                abbreviations.append(abbrev)
                break
        else:
            print(Fore.YELLOW + f"Warning: No abbreviation found for part of speech '{tag}'")
            unmatched_abbreviations.append(f"Session ID: {session_id} - No abbreviation found for part of speech '{tag}'")
            abbreviations.append(tag)  # Keep original if no match
    return abbreviations
