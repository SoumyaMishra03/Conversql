import re
import stanza
import nltk
from nltk.corpus import stopwords

nltk.download('stopwords')

nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma')

STOPWORDS = set(stopwords.words('english'))

SCHEMA_PHRASES = [
    "asteroids_db", "astronauts_db", "isro_satellites_db", "natural_satellites_db",
    "rockets_db", "space_missions_db", "spacenews_db", "stars_db",
    "neo_reference", "close_approach", "orbit_data",
    "personal_info", "mission_info", "mission_performance",
    "basic_info", "orbital_info", "launch_info",
    "satellite_identity", "satellite_physical",
    "rocket_general_info", "rocket_technical_specs",
    "organizations", "rockets", "missions",
    "news_articles_table", "publishing_info",
    "stars",
    "neo reference id", "name", "absolute magnitude", "est dia in km(min)", "est dia in km(max)",
    "est dia in m(min)", "est dia in m(max)", "est dia in miles(min)", "est dia in miles(max)",
    "est dia in feet(min)", "est dia in feet(max)", "close approach date", "epoch date close approach",
    "relative velocity km per sec", "relative velocity km per hr", "miles per hour",
    "miss dist.(astronomical)", "miss dist.(lunar)", "miss dist.(kilometers)", "miss dist.(miles)",
    "orbiting body", "orbit id", "orbit determination date", "orbit uncertainity",
    "minimum orbit intersection", "jupiter tisserand invariant", "epoch osculation",
    "eccentricity", "semi major axis", "inclination", "asc node longitude", "orbital period",
    "perihelion distance", "perihelion arg", "aphelion dist", "perihelion time", "mean anomaly",
    "mean motion", "equinox", "hazardous",
    "id", "number", "nationwide_number", "original_name", "sex", "year_of_birth", "nationality",
    "military_civilian", "selection", "year_of_selection", "mission_number", "total_number_of_missions",
    "occupation", "year_of_mission", "mission_title", "ascend_shuttle", "in_orbit",
    "descend_shuttle", "hours_mission", "total_hrs_sum", "field21", "eva_hrs_mission", "total_eva_hrs",
    "satellite id(fake)", "name of satellite, alternate names", "current official name of satellite",
    "country/org of un registry", "country of operator/owner", "operator/owner", "users",
    "purpose", "detailed purpose", "class of orbit", "type of orbit", "longitude of geo (degrees)",
    "perigee (km)", "apogee (km)", "eccentricity", "inclination (degrees)", "period (minutes)",
    "launch mass (kg.)", "dry mass (kg.)", "power (watts)", "date of launch", "expected lifetime (yrs.)",
    "contractor", "country of contractor", "launch site", "launch vehicle", "cospar number",
    "norad number", "comments",
    "planet", "gm", "radius", "density", "magnitude", "albedo",
    "cmp", "wiki", "status", "liftoff_thrust", "payload_leo", "stages", "strap_ons",
    "rocket_height_m", "price_musd", "payload_gto", "fairing_diameter_m", "fairing_height_m",
    "organisation", "location", "details", "rocket_status", "price", "mission_status",
    "title", "url", "content", "postexcerpt", "author", "date",
    "star name", "distance", "mass", "luminosity"
]

SCHEMA_VOCAB = set(phrase.lower() for phrase in SCHEMA_PHRASES)

POS_TAGS_MAP = {
    'NN': 'Noun (Singular)', 'NNS': 'Noun (Plural)',
    'NNP': 'Proper Noun (Singular)', 'NNPS': 'Proper Noun (Plural)',
    'VB': 'Verb (Base)', 'VBD': 'Verb (Past)', 'VBG': 'Verb (Gerund)',
    'VBN': 'Verb (Past Participle)', 'VBP': 'Verb (Non-3rd sing. present)', 'VBZ': 'Verb (3rd sing. present)',
    'JJ': 'Adjective', 'JJR': 'Adjective (Comparative)', 'JJS': 'Adjective (Superlative)',
    'RB': 'Adverb', 'RBR': 'Adverb (Comparative)', 'RBS': 'Adverb (Superlative)',
    'IN': 'Preposition/Subordinating Conjunction', 'DT': 'Determiner',
    'PRP': 'Pronoun', 'PRP$': 'Possessive Pronoun',
    'CC': 'Coordinating Conjunction', 'UH': 'Interjection',
    'EX': 'Existential There', 'CD': 'Cardinal Number'
}

def base_tokenize(text):
    text = text.lower()
    return re.findall(r'\b\w+\b', text)

def stanza_tokenize(text):
    doc = nlp(text)
    tokens, pos_tags, lemmas = [], [], []
    for sent in doc.sentences:
        for word in sent.words:
            tokens.append(word.text.lower())
            pos_tags.append((word.text.lower(), word.xpos))
            lemmas.append(word.text.lower() if word.xpos in ('NNP', 'NNPS') else word.lemma.lower())
    return tokens, pos_tags, lemmas

def combine_schema_tokens(tokens):
    combined = []
    i = 0
    max_len = 6
    while i < len(tokens):
        match = False
        for j in range(max_len, 0, -1):
            if i + j <= len(tokens):
                phrase = " ".join(tokens[i:i + j])
                if phrase in SCHEMA_VOCAB:
                    combined.append(phrase)
                    i += j
                    match = True
                    break
        if not match:
            combined.append(tokens[i])
            i += 1
    return combined

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS or t in SCHEMA_VOCAB]

def expand_pos_tags(pos_tags):
    return [(token, POS_TAGS_MAP.get(tag, tag)) for token, tag in pos_tags]

def tokenize(text):
    base_tokens = base_tokenize(text)
    tokens, pos_tags, lemmas = stanza_tokenize(text)
    expanded_pos = expand_pos_tags(pos_tags)
    combined = combine_schema_tokens(lemmas)
    filtered = remove_stopwords(combined)
    return {
        "Base Tokens": base_tokens,
        "POS Tags": expanded_pos,
        "Lemmatized": lemmas,
        "Schema Combined": combined,
        "Final Tokens": filtered
    }
