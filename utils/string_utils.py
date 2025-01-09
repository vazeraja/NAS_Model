import urllib.parse
from urllib.parse import urlparse
import os
import re
from urllib.parse import unquote

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

    @staticmethod
    def sanitize_filename(filename, max_length=100):
        """
        Decode URL-encoded characters, remove special chars that
        can cause issues on Windows, and limit length if necessary.
        """
        # Step 1: decode URL-encoded strings, e.g. '%20' -> ' '
        filename = unquote(filename)

        # Step 2: remove or replace any disallowed characters
        filename = re.sub(r'[<>:"/\\|?*]+', '_', filename)

        # Step 3: optionally limit length
        if len(filename) > max_length:
            # Attempt to preserve file extension if it exists
            name, ext = os.path.splitext(filename)
            filename = (name[: max_length - len(ext)] + ext) if ext else name[:max_length]

        return filename

    @staticmethod
    def make_enum_member(name):
        """
        Convert a string to a valid Enum member name:
        - Uppercase
        - Replace non-alphanumeric characters with underscores
        - Remove leading/trailing underscores
        """
        # Replace non-alphanumeric characters with underscores
        name = re.sub(r'\W+', '_', name)
        # Remove leading/trailing underscores
        name = name.strip('_')
        # Convert to uppercase
        return name.upper()
