import re

class RegexUtils:
    PREDEFINED_PATTERNS = {
        "email" : re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'),
        "ip": re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d{1,2})\.){3}(?:25[0-5]|2[0-4]\d|1?\d{1,2})\b'),
        "phone": re.compile(r'(?:(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4})'),
        "date": re.compile(r'\b(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|\d{4}[-/]\d{1,2}[-/]\d{1,2})\b')
    }

    @staticmethod
    def get_pattern(name):
        return RegexUtils.PREDEFINED_PATTERNS.get(name)
    
    @staticmethod
    def get_all_keys():
        return RegexUtils.PREDEFINED_PATTERNS.keys()