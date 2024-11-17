import discord
from discord.ext import commands

from config import Config
from utilities import Utilities

import json
import re
import logging
import aiohttp
from bs4 import BeautifulSoup
from pdf_downloader import PDFDownloader

config = Config()
logging.basicConfig(level=logging.INFO, filename="cache_debug.log", filemode="w", format="%(asctime)s - %(levelname)s - %(message)s")

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    @commands.command(name="example")
    async def example_command(self, ctx):
        await ctx.send("this is an example command")

    # @commands.command(name="check")
    # async def update_channel_command(self, ctx, channel: discord.TextChannel = None):
    #     previous_channel_map = await Utilities.get_channel_map()
    #     current_channel_map = await Utilities.cache_channel_data(channel)
    #
    #     previous_channel_dict = previous_channel_map.get(channel.name, {})
    #     current_channel_dict = current_channel_map.get(channel.name, {})
    #
    #     report = await Utilities.compare_dicts(previous_channel_dict, current_channel_dict)
    #     await ctx.send(report)

    @commands.command(name="report")
    async def report_command(self, ctx, channel: discord.TextChannel = None):
        links_by_domain = await Utilities.get_links_by_domain(channel)
        null_links = await Utilities.get_null_links(channel)

        total_links = 0
        for domain in links_by_domain:
            total_links += len(links_by_domain[domain])

        empty_links_text = "\n".join(null_links)
        summary_text = "\n".join(f"{domain}: {len(links)} links" for domain, links in links_by_domain.items())

        summary_embed = discord.Embed(
            title=f"Summary of Links by Domain in {channel.name}",
            description=f"Summary: {summary_text} \n"
                        f"Total Links: {total_links} \n",
            color=discord.Color.green()
        )
        await ctx.send(embed=summary_embed)

        empty_links_embed = discord.Embed(
            description=f"Empty Links: {empty_links_text}",
            color=discord.Color.red()
        )
        await ctx.send(embed=empty_links_embed)

    @commands.command(name="cache")
    async def cache_command(self, ctx, channel: discord.TextChannel = None):
        if ctx.channel.id != 1299034004472860703:
            return  # Only allow command in bot_testing

        logging.info("Starting caching process for channel: %s", channel.name if channel else "Current Channel")

        target_channel = channel or ctx.channel
        url_pattern = r'(https?://[^\s]+)'
        channel_map = await Utilities.get_channel_map()

        progress_message = await ctx.send("Starting caching process...")
        total_messages = 0
        async for _ in target_channel.history(limit=None):
            total_messages += 1

        logging.info("Total messages in channel %s: %d", target_channel.name, total_messages)

        processed_messages = 0
        update_interval = 5  # Number of messages to process before updating the progress

        async for message in target_channel.history(limit=None):  # Use None for no specific limit
            try:
                found_links = re.findall(url_pattern, message.content)
                logging.info("Processing message ID %s, found %d links", message.id, len(found_links))

                for link in found_links:
                    channel_name = target_channel.name

                    # Group links by channel
                    if channel_name not in channel_map:
                        channel_map[channel_name] = {}

                    # Retrieve the PDF URL and store it directly in the links_by_channel dictionary
                    pdf_url = await PDFDownloader.get_pdf_url(link)
                    channel_map[channel_name][link] = pdf_url

            except Exception as e:
                logging.error("Error processing message ID %s: %s", message.id, str(e))

            processed_messages += 1

            # Update the progress message at specified intervals
            if processed_messages % update_interval == 0 or processed_messages == total_messages:
                progress = int((processed_messages / total_messages) * 100)
                progress_bar = f"[{'#' * (progress // 10)}{'-' * (10 - progress // 10)}]"  # 10-segment bar
                await progress_message.edit(content=f"Caching in progress... {progress}% {progress_bar}")

        # Save the generated link-to-pdf map (links_by_channel) to a JSON file
        json_file_path = "channel_map.json"
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(channel_map, json_file, indent=4)

        await progress_message.edit(content="Caching completed! Links and PDF URLs have been saved.")
        logging.info("Caching process completed.")


async def setup(bot):
    await bot.add_cog(Commands(bot))
