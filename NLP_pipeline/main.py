from tokenizer_stanza import tokenize, SCHEMA_PHRASES
from schema_entity_recognizer import schema_entity_recognizer
from value_entity_recognizer import value_entity_recognizer

queries = [
    "List all astronauts who participated in missions and logged eva_hrs_missions above 10.",
    "Show me the satellites launched after 2010 that orbit around Mars.",
    "Which rockets were flying and carrying payloads heavier than 5000 kg?",
    "Find the rocket with the highest payload_leo from rockets_db.",
    "What are the most luminous stars in the stars_db?",
    "Display star names, distances and luminosities of stars closer than 50 light years.",
    "Give details about organizations operating missions in the space_missions_db.",
    "Which astronauts were selected in 2005 and went on missions later?",
    "What satellites were operated by ISRO and launched in 2019?",
    "Give me the albedo values for satellites that were orbiting Jupiter.",
    "Tell me which missions have been completed by NASA astronauts.",
    "I'm curious about the perihelion times and orbit id from orbit_data in asteroids."
]

for query in queries:
    print("=" * 80)
    print(f"Query: {query}")
    
    tokenized = tokenize(query)
    filtered_tokens = tokenized["Final Tokens"]

    schema_entities = schema_entity_recognizer(filtered_tokens, SCHEMA_PHRASES)
    value_entities = value_entity_recognizer(query)

    print("Filtered Tokens:", filtered_tokens)
    print("→ Schema Entities:")
    for entity in schema_entities:
        print("   ", entity)

    print("→ Value Entities:")
    for ent in value_entities:
        print("   ", {
            'type': ent[0],
            'value': ent[1],
            'start': ent[2],
            'end': ent[3]
        })
