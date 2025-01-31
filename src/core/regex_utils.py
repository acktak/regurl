import re

class RegexUtils:
    PREDEFINED_PATTERNS = {
        "IP Address": re.compile(r"\b\d{1,3}(\.\d{1,3}){3}\b"),
        "Phone Number": re.compile(r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b"),
        "Time": re.compile(r"\b\d{1,2}:\d{2}(?:\s?[APap][Mm])?\b"),
        "Date": re.compile(r"\b\d{1,2}/\d{1,2}/\d{4}\b")
    }

    @staticmethod
    def get_pattern(name):
        return RegexUtils.PREDEFINED_PATTERNS.get(name)
