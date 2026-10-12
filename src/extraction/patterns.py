import re

# Patterns used to extract information from a resume.

# Matches a name with at least two words, each starting with a capital letter.

NAME_PATTERN = re.compile(
    r"^(?P<name>[A-Z][A-Za-z'\-]+(?:[ ][A-Z][A-Za-z'\-]+)+)[ ]*$",
    re.MULTILINE,
)

# Matches an email address.
EMAIL_PATTERN = re.compile(
    r"(?P<email>[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})"
)

# Matches a phone number with or without an international prefix.
PHONE_PATTERN = re.compile(
    r"(?P<phone>(?:\+\d{1,3}[ \-]?)?\d{3}[ \-]?\d{3}[ \-]?\d{3,4})"
)


# Extracts the location and role from their respective lines.
LOCATION_PATTERN = re.compile(r"^Location:[ ]*(?P<location>.+)$", re.MULTILINE)
ROLE_PATTERN = re.compile(r"^Role:[ ]*(?P<role>.+)$", re.MULTILINE)


# Extracts the summary until the next blank line or the end of the text.
SUMMARY_PATTERN = re.compile(
    r"^Summary:[ ]*\n(?P<summary>.+?)(?:\n[ ]*\n|\Z)",
    re.MULTILINE | re.DOTALL,
)


# Matches a degree, field of study, institution and graduation year.
EDUCATION_PATTERN = re.compile(
    r"^(?P<degree>BSc|MSc|PhD|BA|MA|Technologist)[ ]+in[ ]+(?P<field>[^,\n]+),"
    r"[ ]*(?P<institution>[^,\n]+),[ ]*(?P<year>\d{4})[ ]*$",
    re.MULTILINE,
)


# Extracts the job title, organization and years of experience.
EXPERIENCE_PATTERN = re.compile(
    r"^(?P<title>[^|\n]+?)[ ]*\|[ ]*(?P<organization>[^|\n]+?)[ ]*\|"
    r"[ ]*(?P<years>\d+)[ ]+years?[ ]*$",
    re.MULTILINE,
)


# Matches responsibilities written as a list with hyphens.
RESPONSIBILITY_PATTERN = re.compile(
    r"^-[ ]+(?P<responsibility>.+?)[ ]*$", re.MULTILINE
)

# Extracts the total years of experience from the text.
TOTAL_EXPERIENCE_PATTERN = re.compile(
    r"(?P<years>\d+)[ ]+years?[ ]+of[ ]+experience"
)

# Extracts the technical skills section until the next blank line or the end.
SKILLS_BLOCK_PATTERN = re.compile(
    r"^Technical Skills:[ ]*\n(?P<skills>.+?)(?:\n[ ]*\n|\Z)",
    re.MULTILINE | re.DOTALL,
)

# Splits the skills section into individual skills.
SKILL_ITEM_PATTERN = re.compile(r"[^,;\n]+")