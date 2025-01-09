import discord
import urllib.parse
from collections import Counter
from urllib.parse import urlparse

from utils.discord_utils import DiscordUtils


class DictUtils:


    @staticmethod
    async def get_pdfs_for_domain(domain):
        channel_map = await DiscordUtils.get_channel_map()

        link_urls = []
        pdf_urls = []

        for channel, items in channel_map.items():
            channel_dict = channel_map.get(channel, {})
            for url, pdf in channel_dict.items():
                if urlparse(url).netloc == domain:
                    if domain == 'library.lol':
                        link_urls.append(url.replace("lol", "gift"))
                    link_urls.append(url)
                    pdf_urls.append(pdf)

        return link_urls, pdf_urls

    @staticmethod
    async def extract_and_sort_domains_by_frequency():
        domain_counter = Counter()
        data = await DiscordUtils.get_channel_map()

        # Iterate through all branches and their URLs
        for branch, links in data.items():
            for url in links.keys():
                domain = urlparse(url).netloc
                if domain:
                    domain_counter[domain] += 1

        # Sort domains by frequency (descending) and then alphabetically
        sorted_domains = sorted(domain_counter.items(), key=lambda x: (-x[1], x[0]))

        return sorted_domains

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
