# spell_corrector.py

import logging
from language_tool_python import LanguageTool
import stanza
from tokenizer_stanza import SCHEMA_PHRASES

# ─── Init LanguageTool ───────────────────────────────────────────────────────
tool = LanguageTool('en-US')

# ─── Init stanza NER ─────────────────────────────────────────────────────────
# Make sure you’ve run once:
#   >>> import stanza
#   >>> stanza.download('en')
nlp = stanza.Pipeline(lang='en', processors='tokenize,ner', use_gpu=False, logger=False)

# ─── Build protected domain terms (lowercased) ────────────────────────────────
DOMAIN_TERMS = {t.lower() for t in SCHEMA_PHRASES}

def correct_query(text: str) -> str:
    """
    1) Run LanguageTool to fix spelling/grammar
    2) Use stanza NER to find all proper‐noun tokens
    3) Protect domain terms, acronyms, and any NER token from being “fixed”
    """
    # 1) ask LanguageTool to auto-correct
    try:
        fixed = tool.correct(text)
    except Exception as e:
        logging.warning(f"LanguageTool failed: {e}")
        fixed = text

    # 2) run stanza NER on the original text to grab proper names
    doc = nlp(text)
    ner_tokens = {w.text.lower()
                  for ent in doc.ents
                  for w in ent.words}

    # 3) re-tokenize corrected text, but skip any protected tokens
    out = []
    for tok in fixed.split():
        lt = tok.lower()

        # skip if domain term, acronym, or proper name
        if lt in DOMAIN_TERMS or tok.isupper() or lt in ner_tokens:
            out.append(tok)
            continue

        # otherwise, keep LanguageTool’s version
        out.append(tok)

    return " ".join(out)