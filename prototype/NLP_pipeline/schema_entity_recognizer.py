import json
import re
import os
from nltk.corpus import wordnet as wn

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_MAP_PATH = os.path.join(MODULE_DIR, 'base_synonym_map.json')

def normalize(text):
    return re.sub(r'[\\s_().]', '', text.lower())

def generate_filtered_wordnet_synonyms(term, threshold=1.0):
    normalized_term = normalize(term)
    synonyms = set()
    synsets = wn.synsets(term, pos=wn.NOUN)
    if not synsets:
        return []
    base_synset = synsets[0]
    for syn in synsets:
        sim = base_synset.wup_similarity(syn)
        if sim and sim >= threshold:
            for lemma in syn.lemmas():
                lemma_name = normalize(lemma.name())
                if lemma_name != normalized_term:
                    synonyms.add(lemma_name)
    return list(synonyms)

def expand_with_wordnet(schema_terms, base_map):
    expanded_map = {normalize(k): v for k, v in base_map.items()}
    normalized_schema = {normalize(term): term for term in schema_terms}
    wordnet_only_map = {}
    for key, original_value in base_map.items():
        syns = generate_filtered_wordnet_synonyms(key)
        for syn in syns:
            if syn not in expanded_map:
                expanded_map[syn] = original_value
                wordnet_only_map[syn] = original_value
    with open(os.path.join(MODULE_DIR, 'expanded_wordnet_synonyms.json'), 'w') as f:
        json.dump(wordnet_only_map, f, indent=2)
    return expanded_map, wordnet_only_map

def schema_entity_recognizer(tokens, schema_terms, synonym_map=None, wordnet_only_map=None):
    if synonym_map is None:
        with open(BASE_MAP_PATH, 'r') as f:
            base_map = json.load(f)
        synonym_map, wordnet_only_map = expand_with_wordnet(schema_terms, base_map)

    def classify_entity_type(schema_term):
        databases = {
            'asteroids_db', 'astronauts_db', 'isro_satellites_db',
            'natural_satellites_db', 'rockets_db', 'space_missions_db',
            'spacenews_db', 'stars_db'
        }
        tables = {
            'neo_reference', 'close_approach', 'orbit_data',
            'personal_info', 'mission_info', 'mission_performance',
            'basic_info', 'orbital_info', 'launch_info',
            'satellite_identity', 'satellite_physical',
            'rocket_general_info', 'rocket_technical_specs',
            'organizations', 'rockets', 'missions',
            'news_articles_table', 'publishing_info', 'stars'
        }
        columns = {
            'id', 'name', 'title', 'date', 'status', 'location', 'details',
            'neo reference id', 'absolute magnitude', 'est dia in km(min)', 'est dia in km(max)',
            'est dia in m(min)', 'est dia in m(max)', 'est dia in miles(min)', 'est dia in miles(max)',
            'est dia in feet(min)', 'est dia in feet(max)', 'close approach date', 'epoch date close approach',
            'relative velocity km per sec', 'relative velocity km per hr', 'miles per hour',
            'miss dist.(astronomical)', 'miss dist.(lunar)', 'miss dist.(kilometers)', 'miss dist.(miles)',
            'orbiting body', 'orbit id', 'orbit determination date', 'orbit uncertainity',
            'minimum orbit intersection', 'jupiter tisserand invariant', 'epoch osculation',
            'eccentricity', 'semi major axis', 'inclination', 'asc node longitude', 'orbital period',
            'perihelion distance', 'perihelion arg', 'aphelion dist', 'perihelion time', 'mean anomaly',
            'mean motion', 'equinox', 'hazardous', 'number', 'nationwide_number', 'original_name', 'sex',
            'year_of_birth', 'nationality', 'military_civilian', 'selection', 'year_of_selection',
            'mission_number', 'total_number_of_missions', 'occupation', 'year_of_mission', 'mission_title',
            'ascend_shuttle', 'in_orbit', 'descend_shuttle', 'hours_mission', 'total_hrs_sum', 'field21',
            'eva_hrs_mission', 'total_eva_hrs', 'satellite id(fake)', 'name of satellite, alternate names',
            'current official name of satellite', 'country/org of un registry', 'country of operator/owner',
            'operator/owner', 'users', 'purpose', 'detailed purpose', 'class of orbit', 'type of orbit',
            'longitude of geo (degrees)', 'perigee (km)', 'apogee (km)', 'inclination (degrees)',
            'period (minutes)', 'launch mass (kg.)', 'dry mass (kg.)', 'power (watts)', 'date of launch',
            'expected lifetime (yrs.)', 'contractor', 'country of contractor', 'launch site', 'launch vehicle',
            'cospar number', 'norad number', 'comments', 'planet', 'gm', 'radius', 'density', 'magnitude',
            'albedo', 'cmp', 'wiki', 'liftoff_thrust', 'payload_leo', 'stages', 'strap_ons', 'rocket_height_m',
            'price_musd', 'payload_gto', 'fairing_diameter_m', 'fairing_height_m', 'organisation',
            'rocket_status', 'price', 'mission_status', 'url', 'content', 'postexcerpt', 'author',
            'star name', 'distance', 'mass', 'luminosity'
        }
        if schema_term in databases:
            return 'database'
        elif schema_term in tables:
            return 'table'
        elif schema_term in columns:
            return 'column'
        elif schema_term.endswith('_db'):
            return 'database'
        elif '_info' in schema_term or '_data' in schema_term or '_table' in schema_term or schema_term in ['organizations', 'rockets', 'missions', 'stars']:
            return 'table'
        return 'column'

    matched_entities = []
    normalized_schema = {normalize(term): term for term in schema_terms}
    for token in tokens:
        norm_token = normalize(token)
        if norm_token in normalized_schema:
            original = normalized_schema[norm_token]
            matched_entities.append({
                'type': classify_entity_type(original),
                'value': original,
                'matched_token': token,
                'match_method': 'direct'
            })
        elif norm_token in synonym_map:
            mapped = synonym_map[norm_token]
            if mapped in schema_terms:
                match_method = 'wordnet_synonym' if norm_token in wordnet_only_map else 'base_synonym'
                matched_entities.append({
                    'type': classify_entity_type(mapped),
                    'value': mapped,
                    'matched_token': token,
                    'match_method': match_method
                })
    return matched_entities
