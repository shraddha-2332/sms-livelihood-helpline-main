URGENT_KEYWORDS = [
    'emergency', 'urgent', 'no food', 'medical', 'hospital', 'injury',
    'eviction', 'violence', 'abuse', 'threat', 'suicide', 'accident',
    'critical', 'immediate', 'help me', 'danger'
]


def is_urgent_text(text):
    if not text:
        return False
    lowered = text.lower()
    return any(keyword in lowered for keyword in URGENT_KEYWORDS)
