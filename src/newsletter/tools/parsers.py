import re

def clean_text(raw_text):
    if not raw_text:
        return "No abstract available."
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_text)
    cleantext = re.sub(r'\s+', ' ', cleantext)
    return cleantext.strip()

def extract_abstract(entry):
    # --- INTELLIGENT ABSTRACT HUNTING ---
    raw_abstract = "No abstract available."
    
    # 1. Check for Dublin Core description (Used by Wiley/AGU)
    if 'dc_description' in entry and entry.dc_description:
        raw_abstract = entry.dc_description
    # 2. Check for full content payload
    elif 'content' in entry and entry.content:
        raw_abstract = entry.content[0].value
    # 3. Fallback to standard summary
    elif 'summary' in entry and entry.summary:
        raw_abstract = entry.summary
    elif 'description' in entry and entry.description:
        raw_abstract = entry.description
    
    summary = clean_text(raw_abstract)
    return summary
