import discord
from discord.ext import commands

from config import Config
from utilities import Utilities

config = Config()


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    @commands.command(name="example")
    async def example_command(self, ctx):
        await ctx.send("this is an example command")

    @commands.command(name="test")
    async def test_command(self, ctx):
        channel_map = await Utilities.get_link_map()

        link_pdf_pairs = list(channel_map["misesian-branch"].items())
        link, pdf = link_pdf_pairs[0]

        await ctx.send(link)

    # @commands.command(name="report")
    # async def report_command(self, ctx, channel: discord.TextChannel = None):
    #     channel_map = await Utilities.get_link_map()
    #
    #     empty_links = [link for links in links_by_domain.values() for link in links if link not in link_pdf_map]
    #     summary_text = "\n".join(f"{domain}: {len(links)} links" for domain, links in links_by_domain.items())
    #     empty_links_text = "\n".join(empty_links) if empty_links else "None"
    #
    #     summary_embed = discord.Embed(
    #         title=f"Summary of Links by Domain in {target_channel.name}",
    #         description=f"{summary_text}\n\nEmpty Links:\n{empty_links_text}",
    #         color=discord.Color.green()
    #     )
    #     await ctx.send(embed=summary_embed)

    @commands.command(name="cache")
    async def cache_command(self, ctx, channel: discord.TextChannel = None):
        import json
        import re
        from pdf_downloader import PDFDownloader

        if ctx.channel.id != 1299034004472860703:
            return  # Only allow command in bot_testing

        print("getting links")

        # Use the specified channel or default to the current channel if none provided
        target_channel = channel or ctx.channel
        channel_map = {}  # Dictionary to hold links by channel

        # Regular expression pattern for URLs
        url_pattern = r'(https?://[^\s]+)'

        # Fetch messages in the target channel in batches
        async for message in target_channel.history(limit=None):  # Use None for no specific limit
            found_links = re.findall(url_pattern, message.content)
            for link in found_links:
                channel_name = target_channel.name

                # Group links by channel
                if channel_name not in channel_map:
                    channel_map[channel_name] = {}

                # Retrieve the PDF URL and store it directly in the links_by_channel dictionary
                pdf_url = await PDFDownloader.get_pdf_url(link)
                channel_map[channel_name][link] = pdf_url

        # Save the generated link-to-pdf map (links_by_channel) to a JSON file
        json_file_path = "channel_map.json"
        with open(json_file_path, "w", encoding="utf-8") as json_file:
            json.dump(channel_map, json_file, indent=4)

        await ctx.send(f"Links and PDF URLs have been saved to `{json_file_path}`")


async def setup(bot):
    await bot.add_cog(Commands(bot))
