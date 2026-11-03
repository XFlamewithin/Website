"""Small line icons shown beside each topic heading.

Each topic gets an icon automatically from words in its name (see KEYWORDS).
To choose one yourself, add  icon = "<name>"  to any resource in that topic in
resources.toml. Available names are the keys of ICONS below.
"""

# 24×24 outline drawings, stroked in the page's accent colour.
ICONS = {
    "drop": '<path d="M12 3.5c3.4 4 6 7.4 6 10.6a6 6 0 0 1-12 0c0-3.2 2.6-6.6 6-10.6z"/>'
            '<path d="M9.2 14.4a2.9 2.9 0 0 0 2.6 2.8"/>',
    "heart": '<path d="M12 19.5s-7.5-4.4-7.5-10A4.2 4.2 0 0 1 12 7a4.2 4.2 0 0 1 7.5 2.5c0 5.6-7.5 10-7.5 10z"/>',
    "heart-pulse": '<path d="M12 19.5s-7.5-4.4-7.5-10A4.2 4.2 0 0 1 12 7a4.2 4.2 0 0 1 7.5 2.5c0 5.6-7.5 10-7.5 10z"/>'
                   '<path d="M7 12h2.3l1.4-2.4 2.2 4.6 1.4-2.2H17"/>',
    "pulse": '<path d="M2.5 12h4l2.2-5.5 4.3 11 2.3-5.5h6.2"/>',
    "child": '<circle cx="12" cy="5.5" r="2.5"/><path d="M7.5 11.5 12 9.5l4.5 2"/>'
             '<path d="M12 9.5v5.5"/><path d="m9.5 20.5 2.5-5.5 2.5 5.5"/>',
    "dumbbell": '<path d="M6.5 7.5v9M17.5 7.5v9M3.5 10v4M20.5 10v4M6.5 12h11"/>',
    "bone": '<path d="M9.3 7.6 16.4 14.7a2.4 2.4 0 1 1 2.4 3.9 2.4 2.4 0 1 1-3.9 2.4'
            'L7.6 9.3a2.4 2.4 0 1 1-2.4-3.9 2.4 2.4 0 1 1 3.9-2.4z" transform="translate(12 12) scale(.9) translate(-12.2 -12.6)" vector-effect="non-scaling-stroke"/>',
    "ribbon": '<path d="M12 13.2c-1.6-2-3.4-4.3-3.4-6.6a3.4 3.4 0 0 1 6.8 0c0 2.3-1.8 4.6-3.4 6.6z"/>'
              '<path d="m10 10.6-4 9.4 2.8-.8 1.5 2.4 3.4-8.4"/><path d="m14 10.6 4 9.4-2.8-.8-1.5 2.4-1.2-3"/>',
    "pill": '<g transform="rotate(-45 12 12)"><path d="M12 8.5H6.5a3.5 3.5 0 0 0 0 7H12z" fill="currentColor"'
            ' fill-opacity=".3" stroke="none"/><rect x="3" y="8.5" width="18" height="7" rx="3.5"/>'
            '<path d="M12 8.5v7"/></g>',
    "apple": '<path d="M12 7.5c-1.6-1-4.8-1.2-6.2 1.4-1.6 3 .2 8 2.6 10.2 1.2 1.1 2.4.9 3.6.3 1.2.6 2.4.8 3.6-.3'
             ' 2.4-2.2 4.2-7.2 2.6-10.2-1.4-2.6-4.6-2.4-6.2-1.4z"/><path d="M12 7.5c0-2 .8-3.4 2.5-4"/>',
    "lungs": '<path d="M12 4v8M12 10l-2.5 2M12 10l2.5 2"/>'
             '<path d="M8.5 8.5C6 8.5 4 13 4 17c0 1.7 1.3 2.5 2.8 2.2L9.5 18.5V11c0-1.4-.4-2.5-1-2.5z"/>'
             '<path d="M15.5 8.5c2.5 0 4.5 4.5 4.5 8.5 0 1.7-1.3 2.5-2.8 2.2l-2.7-.7V11c0-1.4.4-2.5 1-2.5z"/>',
    "brain": '<path d="M12 5.5v13"/><path d="M12 5.5A2.8 2.8 0 0 0 7 6.8 3 3 0 0 0 5 11.5a3 3 0 0 0 1.2 4.6A2.9 2.9 0 0 0 12 18.5"/>'
             '<path d="M12 5.5a2.8 2.8 0 0 1 5 1.3 3 3 0 0 1 2 4.7 3 3 0 0 1-1.2 4.6A2.9 2.9 0 0 1 12 18.5"/>',
    "stethoscope": '<path d="M6 3.5v5a4 4 0 0 0 8 0v-5"/><path d="M10 12.5v2a4.5 4.5 0 0 0 9 0V13"/>'
                   '<circle cx="19" cy="11" r="2"/>',
    "document": '<path d="M7 3.5h7l4 4v13H7z"/><path d="M14 3.5v4h4M10 12h5M10 15.5h5"/>',
}

# First match wins, so more specific words come first.
KEYWORDS = [
    (("fibrillation", "afib", "arrhythm", "palpitation", "ecg"), "pulse"),
    (("cancer", "screening", "mammo", "polyp"), "ribbon"),
    (("dyslipid", "cardiovascular", "cvd", "blood pressure", "hypertension"), "heart-pulse"),
    (("cholesterol", "lipid", "heart"), "heart"),
    (("iron", "anemia", "anaemia", "blood", "diabetes", "glucose"), "drop"),
    (("child", "kid", "infant", "baby", "pediatric", "paediatric"), "child"),
    (("osteo", "bone", "fracture"), "bone"),
    (("exercise", "rehab", "physio", "arthritis", "knee", "shoulder", "back pain", "fitness"), "dumbbell"),
    (("anticoag", "warfarin", "doac", "medication", "drug", "prescri"), "pill"),
    (("diet", "nutrition", "food", "weight"), "apple"),
    (("asthma", "copd", "lung", "breath", "smok"), "lungs"),
    (("mental", "anxiety", "depress", "sleep", "brain", "memory", "dementia", "headache"), "brain"),
]


def topic_icon(topic, resources):
    """Return the <svg> for a topic: an icon chosen in resources.toml, else by keyword."""
    name = next((r["icon"] for r in resources if r.get("icon")), None)
    if name not in ICONS:
        t = topic.lower()
        name = next((icon for words, icon in KEYWORDS if any(w in t for w in words)), "document")
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'
