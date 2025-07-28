import json
import re
import os
from difflib import SequenceMatcher

from NLP_pipeline.tokenizer_stanza import SCHEMA_PHRASES, SCHEMA_MAP

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
COMP_MAP_PATH = os.path.join(MODULE_DIR, 'json/comparison_operators.json')
INTENT_MAP_PATH = os.path.join(MODULE_DIR, 'json/intent.json')

def normalize(text):
    """Enhanced normalization for better matching"""
    return re.sub(r'[\s_().-]', '', text.lower())

def similarity_score(a, b):
    """Calculate similarity between two strings"""
    return SequenceMatcher(None, a, b).ratio()

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def find_fuzzy_matches(token, schema_terms, threshold=0.8):
    """Find fuzzy matches for tokens that don't match exactly"""
    matches = []
    norm_token = normalize(token)
    
    for term in schema_terms:
        norm_term = normalize(term)
        score = similarity_score(norm_token, norm_term)
        if score >= threshold:
            matches.append((term, score))
    
    return sorted(matches, key=lambda x: x[1], reverse=True)

def get_entity_type_from_schema_map(original_term):
    """Determine entity type using SCHEMA_MAP with enhanced logic"""
    # Check direct mappings first
    if original_term in SCHEMA_MAP["db_to_tables"]:
        return "database"
    elif original_term in SCHEMA_MAP["table_to_db"]:
        return "table"
    elif original_term in SCHEMA_MAP["column_to_table_db"]:
        return "column"
    
    # Check case-insensitive matches
    lower_term = original_term.lower()
    
    # Check databases (case-insensitive)
    for db in SCHEMA_MAP["db_to_tables"]:
        if db.lower() == lower_term:
            return "database"
    
    # Check tables (case-insensitive)
    for table in SCHEMA_MAP["table_to_db"]:
        if table.lower() == lower_term:
            return "table"
    
    # Check columns (case-insensitive)
    for col in SCHEMA_MAP["column_to_table_db"]:
        if col.lower() == lower_term:
            return "column"
    
    return "unknown"

def enhanced_schema_entity_recognizer(tokens, schema_terms=None, enable_fuzzy=True, fuzzy_threshold=0.8):
    """
    Enhanced entity recognizer with fuzzy matching and better context resolution
    """
    comp_map = load_json(COMP_MAP_PATH)
    intent_map = load_json(INTENT_MAP_PATH)

    # Build stop words set
    stop_words = set()
    for phrase in comp_map.keys():
        stop_words.add(normalize(phrase))
    for phrase in intent_map.keys():
        stop_words.add(normalize(phrase))

    # Use provided schema terms or default to SCHEMA_PHRASES
    schema_terms_to_use = schema_terms if schema_terms else SCHEMA_PHRASES
    
    # Create normalized schema mapping
    normalized_schema = {
        normalize(term): term for term in schema_terms_to_use
    }

    matched_entities = []
    unmatched_tokens = []

    for token in tokens:
        norm_token = normalize(token)
        
        # Skip stop words (unless they're schema terms)
        if norm_token in stop_words and norm_token not in normalized_schema:
            continue

        # Direct match
        if norm_token in normalized_schema:
            original = normalized_schema[norm_token]
            ent_type = get_entity_type_from_schema_map(original)
            
            matched_entities.append({
                "type": ent_type,
                "value": original,
                "matched_token": token,
                "match_method": "direct",
                "confidence": 1.0
            })
        
        # Fuzzy matching for unmatched tokens
        elif enable_fuzzy:
            fuzzy_matches = find_fuzzy_matches(token, schema_terms_to_use, fuzzy_threshold)
            
            if fuzzy_matches:
                best_match, confidence = fuzzy_matches[0]
                ent_type = get_entity_type_from_schema_map(best_match)
                
                matched_entities.append({
                    "type": ent_type,
                    "value": best_match,
                    "matched_token": token,
                    "match_method": "fuzzy",
                    "confidence": confidence
                })
            else:
                unmatched_tokens.append(token)
                matched_entities.append({
                    "type": "unmatched",
                    "value": None,
                    "matched_token": token,
                    "match_method": "none",
                    "confidence": 0.0
                })
        else:
            unmatched_tokens.append(token)
            matched_entities.append({
                "type": "unmatched",
                "value": None,
                "matched_token": token,
                "match_method": "none",
                "confidence": 0.0
            })

    return {
        "entities": matched_entities,
        "unmatched_tokens": unmatched_tokens,
        "match_stats": {
            "total_tokens": len(tokens),
            "matched_tokens": len([e for e in matched_entities if e["type"] != "unmatched"]),
            "unmatched_tokens": len(unmatched_tokens)
        }
    }

# Backward compatibility function
def schema_entity_recognizer(tokens, schema_terms=None):
    """Original function signature for backward compatibility"""
    result = enhanced_schema_entity_recognizer(tokens, schema_terms, enable_fuzzy=False)
    return result["entities"]
