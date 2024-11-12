from dotenv import load_dotenv
import asyncio
import re
from itertools import chain
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

import discord
from discord.ext import commands

from Config import Config
from PDFDownloader import PDFDownloader

load_dotenv()

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Allows the bot to read messages
intents.message_content = True  # Required to access message content in recent versions

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Define the channel ID for bot_testing (replace YOUR_CHANNEL_ID with the actual ID)
BOT_TESTING_CHANNEL_ID = 1299034004472860703  # e.g., 123456789012345678


@bot.command()
async def extract(ctx, url: str = None):
    pdf_link = PDFDownloader.get_pdf_url(url)

    embed = discord.Embed(
        title=f"Extracted Link",
        color=discord.Color.blue()
    )
    embed.add_field(name="", value=pdf_link, inline=False)
    await ctx.send(embed=embed)


@bot.command()
async def extract_librarylol(ctx, url: str = None):
    pdf_url = await PDFDownloader.get_pdf_url_librarylol(url, "D:/Github/NAS_Model/books/discord")

    embed = discord.Embed(
        title="Extracted Link",
        color=discord.Color.blue()
    )
    embed.add_field(name="PDF URL", value=pdf_url, inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def get_links(ctx, channel: discord.TextChannel = None):
    if ctx.channel.id != BOT_TESTING_CHANNEL_ID:
        return  # Only allow command in bot_testing

    print("getting links")

    # Use the specified channel or default to the current channel if none provided
    target_channel = channel or ctx.channel
    links_by_domain = {}

    # Regular expression pattern for URLs
    url_pattern = r'(https?://[^\s]+)'

    # Fetch messages in the target channel in batches
    async for message in target_channel.history(limit=None):  # Use None for no specific limit
        found_links = re.findall(url_pattern, message.content)
        for link in found_links:
            # Parse the domain from each link
            domain = urlparse(link).netloc
            if domain not in links_by_domain:
                links_by_domain[domain] = []
            links_by_domain[domain].append(link)

    # If links were found, display them in an embed
    if links_by_domain:
        # for domain, links in links_by_domain.items():
        #     # Create an embed with each domain's links
        #     for i in range(0, len(links), 5):  # Send in batches of 5 to fit Discord's character limit
        #         embed = discord.Embed(
        #             title=f"Links found in {target_channel.name} - {domain}",
        #             color=discord.Color.blue()
        #         )
        #         batch = links[i:i + 5]  # Create a batch of links
        #         link_text = "\n".join(batch)
        #         embed.add_field(name="Links", value=link_text, inline=False)
        #         await ctx.send(embed=embed)
        #
        # Now, let's extract PDF URLs for specific domains (mises.org and library.lol)
        mises_links = []
        library_lol_links = []

        for link in links_by_domain.get('mises.org', []):
            pdf_url = await PDFDownloader.get_pdf_url(link)
            mises_links.append(f"Mises PDF: {pdf_url}")

        for link in links_by_domain.get('library.lol', []):
            pdf_url = await PDFDownloader.get_pdf_url(link)
            library_lol_links.append(f"Liblol PDF: {pdf_url}")

        # Send the extracted PDF links for mises.org in batches
        if mises_links:
            for i in range(0, len(mises_links), 5):  # Batch size of 5
                batch = mises_links[i:i + 5]
                embed = discord.Embed(
                    title="Extracted PDF Links from mises.org",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Links", value="\n".join(batch), inline=False)
                await ctx.send(embed=embed)

        # Send the extracted PDF links for library.lol in batches
        if library_lol_links:
            for i in range(0, len(library_lol_links), 1):  # Batch size of 5
                batch = library_lol_links[i:i + 1]
                embed = discord.Embed(
                    title="Downloaded PDF Links from library.lol",
                    color=discord.Color.blue()
                )
                embed.add_field(name="Links", value="\n".join(batch), inline=False)
                await ctx.send(embed=embed)


        # Send a summary of domains and link counts at the end
        summary_text = "\n".join(f"{domain}: {len(links)} links" for domain, links in links_by_domain.items())
        summary_embed = discord.Embed(
            title=f"Summary of Links by Domain in {target_channel.name}",
            description=summary_text,
            color=discord.Color.green()
        )
        await ctx.send(embed=summary_embed)

    else:
        await ctx.send(f"No links found in {target_channel.mention}.")

@bot.event
async def on_ready():
    print(f'Bot is ready. Logged in as {bot.user}')


async def main():
    config = Config()
    try:
        await bot.start(config.DISCORD_API_KEY)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Bot is shutting down...")
    finally:
        await bot.close()  # Ensures bot disconnects even on interruption


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
