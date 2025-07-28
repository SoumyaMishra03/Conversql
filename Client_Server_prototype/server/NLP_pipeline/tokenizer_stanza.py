import re
import stanza
import nltk
import json
from nltk.corpus import stopwords

nltk.download('stopwords')

lang = "en"

SCHEMA_PHRASES = set()
SCHEMA_MAP = {
    "db_to_tables": {},
    "table_to_db": {},
    "table_to_columns": {},
    "column_to_table_db": {},
}

with open("plugin_schema.json", "r") as f:
    plugin_data = json.load(f)
    for db in plugin_data["databases"]:
        db_name = db["name"].lower()
        SCHEMA_PHRASES.add(db_name)
        SCHEMA_MAP["db_to_tables"][db_name] = []

        for table in db["tables"]:
            table_name = table["name"].lower()
            SCHEMA_PHRASES.add(table_name)
            SCHEMA_MAP["db_to_tables"][db_name].append(table_name)
            SCHEMA_MAP["table_to_db"][table_name] = db_name
            SCHEMA_MAP["table_to_columns"][table_name] = []

            for col in table["columns"]:
                col_name = col.lower()
                SCHEMA_PHRASES.add(col_name)
                SCHEMA_MAP["table_to_columns"][table_name].append(col_name)
                SCHEMA_MAP["column_to_table_db"][col_name] = (db_name, table_name)

def get_pipeline(language):
    return stanza.Pipeline(language, processors='tokenize,pos,lemma')

nlp = get_pipeline(lang)

def set_language(new_lang):
    global lang, nlp, STOPWORDS
    lang = new_lang
    nlp = get_pipeline(lang)
    if lang == "hi":
        STOPWORDS = set()
    else:
        STOPWORDS = set(stopwords.words('english'))

set_language(lang)
STOPWORDS = set(stopwords.words('english'))

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
                if phrase in SCHEMA_PHRASES:
                    combined.append(phrase)
                    i += j
                    match = True
                    break
        if not match:
            combined.append(tokens[i])
            i += 1
    return combined

def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS or t in SCHEMA_PHRASES]

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
