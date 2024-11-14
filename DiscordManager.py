from discord.ext.commands.parameters import empty
from dotenv import load_dotenv
import asyncio
from itertools import chain
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests

import discord
from discord.ext import commands

from config import Config
from pdf_downloader import PDFDownloader
from utilities import Utilities

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
