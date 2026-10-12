from .patterns import (
    EDUCATION_PATTERN,
    EMAIL_PATTERN,
    EXPERIENCE_PATTERN,
    LOCATION_PATTERN,
    NAME_PATTERN,
    PHONE_PATTERN,
    RESPONSIBILITY_PATTERN,
    ROLE_PATTERN,
    SKILLS_BLOCK_PATTERN,
    SKILL_ITEM_PATTERN,
    SUMMARY_PATTERN,
    TOTAL_EXPERIENCE_PATTERN,
)


def _first(pattern, text, group):
    """Return the named group of the first match, or None if there is none."""
    match = pattern.search(text)
    if match is None:
        return None
    return match.group(group).strip()


def extract_contact(text):
    """Extract the contact information of the candidate.
    Returns a dictionary with the keys `name`, `email`, `phone`, `location` and `role`.  A key is None when the corresponding pattern does not match.
    """
    return {
        "name": _first(NAME_PATTERN, text, "name"),
        "email": _first(EMAIL_PATTERN, text, "email"),
        "phone": _first(PHONE_PATTERN, text, "phone"),
        "location": _first(LOCATION_PATTERN, text, "location"),
        "role": _first(ROLE_PATTERN, text, "role"),
    }


def extract_summary(text):
    """Extract the summary paragraph, as a single line of text."""
    raw = _first(SUMMARY_PATTERN, text, "summary")
    if raw is None:
        return None
    return " ".join(raw.split())


def extract_education(text):
    """Extract the academic qualifications.
    Returns a list of dictionaries with the keys `degree`, `field`, `institution` and `year`.
    """
    records = []
    for match in EDUCATION_PATTERN.finditer(text):
        records.append({
            "degree": match.group("degree"),
            "field": match.group("field").strip(),
            "institution": match.group("institution").strip(),
            "year": int(match.group("year")),
        })
    return records


def extract_experience(text):
    """Extract the professional experience entries.
    Returns a list of dictionaries with the keys `title`, `organization`, `years` and `responsibilities`.
    """
    entries = []
    matches = list(EXPERIENCE_PATTERN.finditer(text))
    for index, match in enumerate(matches):
        start = match.end()
        if index + 1 < len(matches):
            end = matches[index + 1].start()
        else:
            end = len(text)
        block = text[start:end]
        responsibilities = [
            item.group("responsibility")
            for item in RESPONSIBILITY_PATTERN.finditer(block)
        ]
        entries.append({
            "title": match.group("title").strip(),
            "organization": match.group("organization").strip(),
            "years": int(match.group("years")),
            "responsibilities": responsibilities,
        })
    return entries


def extract_total_experience(text):
    """Extract the total number of years of experience, or None."""
    raw = _first(TOTAL_EXPERIENCE_PATTERN, text, "years")
    if raw is None:
        return None
    return int(raw)


def extract_skills(text):
    """Extract the raw technical skills, exactly as written in the resume."""
    block = _first(SKILLS_BLOCK_PATTERN, text, "skills")
    if block is None:
        return []
    skills = []
    for item in SKILL_ITEM_PATTERN.finditer(block):
        skill = item.group().strip().rstrip(".")
        if skill:
            skills.append(skill)
    return skills


def extract(text):
    """Run the whole extraction stage over the text of a resume."""
    data = extract_contact(text)
    data["summary"] = extract_summary(text)
    data["education"] = extract_education(text)
    data["experience"] = extract_experience(text)
    data["total_experience_years"] = extract_total_experience(text)
    data["raw_skills"] = extract_skills(text)
    return data