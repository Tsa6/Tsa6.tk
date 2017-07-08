html_replacements = [
    ('&', '&amp;'),
    ('<', '&lt;'),
    ('>', '&gt;'),
    ('"','&quot;'),
    ("'",'&#x27;'),
    ('/','&#x2F;'),
]

def sanitize_html(text):
    return custom_sanitize(text,html_replacements)

def custom_sanitize(text,replacements):
    for repl in replacements:
        text = text.replace(repl[0], repl[1])
    return text