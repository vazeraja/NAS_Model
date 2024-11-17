import asyncio
import urllib.parse
import re
import json
import discord
from urllib.parse import urlparse
from pdf_downloader import PDFDownloader


class Utilities:

    @staticmethod
    async def printall(items):
        for item in items:
            print(f"- {item}")

    @staticmethod
    async def compare_dicts(dict1, dict2):
        # Check for equality
        if dict1 == dict2:
            return "The channels are equal."

        # Find differing key-value pairs
        differences = {key: value for key, value in dict1.items() if dict2.get(key) != value}

        # Find missing keys in each dictionary
        missing_in_dict1 = set(dict2.keys()) - set(dict1.keys())
        missing_in_dict2 = set(dict1.keys()) - set(dict2.keys())

        result = []
        if differences:
            result.append(f"Differences in key-value pairs: {differences}")
        if missing_in_dict1:
            result.append(f"Keys missing in dict1: {missing_in_dict1}")

        return result

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
    async def get_channel_map():
        import os
        import json

        channel_map = {}
        json_file_path = "channel_map.json"
        if os.path.exists(json_file_path):
            with open(json_file_path, "r", encoding="utf-8") as json_file:
                channel_map = json.load(json_file)
        return channel_map

    @staticmethod
    async def get_null_links(target_channel: discord.TextChannel):
        channel_map = await Utilities.get_channel_map()
        channel_dict = channel_map.get(target_channel.name, {})

        null_links = []

        for key, value in channel_dict.items():
            if value is None or value == "":
                null_links.append(key)

        return null_links

    @staticmethod
    async def get_links_by_domain(target_channel: discord.TextChannel):
        channel_map = await Utilities.get_channel_map()
        channel_dict = channel_map.get(target_channel.name, {})

        links_by_domain = {}

        for link in channel_dict.keys():
            domain = urlparse(link).netloc

            if domain not in links_by_domain:
                links_by_domain[domain] = []

            links_by_domain[domain].append(link)

        return links_by_domain

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
