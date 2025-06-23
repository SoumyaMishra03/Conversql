def schema_entity_recognizer(tokens, schema_terms, synonym_map=None):
    if synonym_map is None:
        synonym_map = {}

    matched_entities = []

    normalized_schema = {term.lower().replace("_", ""): term for term in schema_terms}

    for token in tokens:
        base = token.lower().replace("_", "")
        if base in normalized_schema:
            original = normalized_schema[base]
            matched_entities.append({
                'type': 'table' if original.endswith('_db') else 'column',
                'value': original
            })
        elif token in synonym_map:
            mapped = synonym_map[token]
            if mapped in schema_terms:
                matched_entities.append({
                    'type': 'table' if mapped.endswith('_db') else 'column',
                    'value': mapped
                })

    return matched_entities
