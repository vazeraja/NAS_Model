import discord
import urllib.parse
from urllib.parse import urlparse

from utils.discord_utils import DiscordUtils


class DictUtils:
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
    async def get_null_links(channel_name):
        channel_map = await DiscordUtils.get_channel_map()
        channel_dict = channel_map.get(channel_name, {})

        null_links = []

        for key, value in channel_dict.items():
            if value is None or value == "":
                null_links.append(key)

        return null_links

    @staticmethod
    async def get_links_by_domain(channel_name):
        channel_map = await DiscordUtils.get_channel_map()
        channel_dict = channel_map.get(channel_name, {})

        links_by_domain = {}

        for link in channel_dict.keys():
            domain = urlparse(link).netloc

            if domain not in links_by_domain:
                links_by_domain[domain] = []

            links_by_domain[domain].append(link)

        return links_by_domain
