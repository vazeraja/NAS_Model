import asyncio
import urllib.parse
import re

class Utilities:

    @staticmethod
    async def printall(items):
        for item in items:
            print(f"- {item}")

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
    async def confirm_and_run(func, prompt, *args, **kwargs):
        """
        Prompts the user to confirm before running the specified function.

        :param func: The function to run if confirmed.
        :param prompt: The prompt that will be displayed to the user.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        """

        response = input(f"{prompt} (Y/N): ").strip().upper()

        if response == 'Y' or response == 'y':
            # Check if the function is awaitable
            if asyncio.iscoroutinefunction(func):
                await func(*args, **kwargs)
            else:
                func(*args, **kwargs)
            return True
        elif response == 'N' or response == 'n':
            return False
        else:
            print("Invalid input. Please enter 'Y' or 'N'.")
            return await Utilities.confirm_and_run(func, prompt, *args, **kwargs)  # Retry on invalid input
