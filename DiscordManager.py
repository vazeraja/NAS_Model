import asyncio
import os
from dotenv import load_dotenv

import re
import discord
from discord.ext import commands

from Config import Config

load_dotenv()

# Define the intents
intents = discord.Intents.default()
intents.messages = True  # Allows the bot to read messages
intents.message_content = True  # Required to access message content in recent versions

# Initialize the bot with command prefix and intents
bot = commands.Bot(command_prefix="!", intents=intents)

# Define the channel ID for bot_testing (replace YOUR_CHANNEL_ID with the actual ID)
BOT_TESTING_CHANNEL_ID = 1299034004472860703  # e.g., 123456789012345678

# Command to retrieve all links from a specified channel and display them in an embed
@bot.command()
async def get_links(ctx, channel: discord.TextChannel = None):
    if ctx.channel.id != BOT_TESTING_CHANNEL_ID:
        return  # Only allow command in bot_testing

    # Use the specified channel or default to the current channel if none provided
    target_channel = channel or ctx.channel
    links = []

    # Regular expression pattern for URLs
    url_pattern = r'(https?://[^\s]+)'

    # Fetch messages in the target channel in batches
    async for message in target_channel.history(limit=None):  # Use None for no specific limit
        found_links = re.findall(url_pattern, message.content)
        if found_links:
            links.extend(found_links)

    unique_links = list(set(links))

    # If links were found, display them in an embed
    if unique_links:
        # Send unique_links in batches within embeds to avoid Discord’s character limit
        for i in range(0, len(unique_links), 5):  # Adjust batch size if needed
            if i == 0:
                embed = discord.Embed(
                    title=f"Links found in {target_channel.name}",
                    color=discord.Color.blue()
                )
            else:
                embed = discord.Embed(
                    title="",
                    color=discord.Color.blue()
                )

            batch = unique_links[i:i + 5]  # Create a batch ofunique_links
            link_text = "\n".join(batch)
            embed.add_field(name="Links", value=link_text, inline=False)

            await ctx.send(embed=embed)

        await ctx.send(embed=discord.Embed(title=f"Final Results: \nTotal Links: {len(unique_links)}", color=discord.Color.blue()))
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
