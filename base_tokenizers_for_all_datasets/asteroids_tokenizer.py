import re

schema_phrases = [
    # Table names
    "neo reference",
    "close approach",
    "orbit data",

    # neo_reference
    "name",
    "absolute magnitude",
    "est dia in km(min)",
    "est dia in km(max)",
    "est dia in m(min)",
    "est dia in m(max)",
    "est dia in miles(min)",
    "est dia in miles(max)",
    "est dia in feet(min)",
    "est dia in feet(max)",

    # Columns from close_approach
    "neo reference id",
    "close approach date",
    "epoch date close approach",
    "relative velocity km per sec",
    "relative velocity km per hr",
    "miles per hour",
    "miss dist.(astronomical)",
    "miss dist.(lunar)",
    "miss dist.(kilometers)",
    "miss dist.(miles)",

    # Columns from orbit_data
    "neo reference id",
    "orbiting body",
    "orbit id",
    "orbit determination date",
    "orbit uncertainity",
    "minimum orbit intersection",
    "jupiter tisserand invariant",
    "epoch osculation",
    "eccentricity",
    "semi major axis",
    "inclination",
    "asc node longitude",
    "orbital period",
    "perihelion distance",
    "perihelion arg",
    "aphelion dist",
    "perihelion time",
    "mean anomaly",
    "mean motion",
    "equinox",
    "hazardous"
]

def base_tokenize(text):
    text = text.lower()
    tokens = re.findall(r'\b\w+\b', text)
    return tokens

def combine_schema_tokens(tokens):
    combined_tokens = []
    i = 0
    max_phrase_length = 5 
    while i < len(tokens):
        match_found = False
        for j in range(max_phrase_length, 0, -1):
            if i + j <= len(tokens):
                phrase = " ".join(tokens[i:i+j])
                if phrase in schema_phrases:
                    combined_tokens.append(phrase)
                    i += j
                    match_found = True
                    break
        if not match_found:
            combined_tokens.append(tokens[i])
            i += 1
    return combined_tokens

def tokenize(text):
    tokens = base_tokenize(text)
    tokens = combine_schema_tokens(tokens)
    return tokens

if __name__ == '__main__':
    queries = [
        "Find the neo reference id and absolute magnitude for asteroid Apollo.",
        "What is the close approach date and relative velocity km per sec of asteroid 2023 FK?",
        "List orbital period, eccentricity, and mean anomaly for all known hazardous asteroids.",
        "Show miss dist.(kilometers) and miles per hour for close approach of asteroid 99942 Apophis.",
        "What is the perihelion distance and eccentricity for orbit data of asteroid Bennu?"
    ]

    for query in queries:
        tokens = tokenize(query)
        print("Query:", query)
        print("Tokens:", tokens)
        print("-" * 60)
