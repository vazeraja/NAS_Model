import urllib.parse
from urllib.parse import urlparse
import re


class StringUtils:

    @staticmethod
    def is_empty(string):
        return not string or string.strip() == ""

    @staticmethod
    def clean_filename(url_filename: str) -> str:
        # Decode URL-encoded characters
        decoded_filename = urllib.parse.unquote(url_filename)

        # Remove unnecessary symbols (e.g., parentheses around author or publisher info)
        cleaned_filename = re.sub(r'[\(\)%]', '', decoded_filename)

        # Replace multiple spaces or punctuation with a single space
        cleaned_filename = re.sub(r'[\s_]+', ' ', cleaned_filename)

        # Capitalize each word for readability (optional)
        cleaned_filename = cleaned_filename.title().strip()

        return cleaned_filename
