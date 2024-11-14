import discord
from discord.ext import commands

from config import Config

config = Config()

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config()

    @commands.command(name="example")
    async def example_command(self, ctx):
        await ctx.send("this is an example command")

    @commands.command(name="getlinks")
    async def get_links(self, ctx, channel: discord.TextChannel = None):
        import json
        import re
        from urllib.parse import urlparse
        from pdf_downloader import PDFDownloader
        from utilities import Utilities

        if ctx.channel.id != 1299034004472860703:
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

        # Dictionary to hold the final link-to-pdf_url mapping for JSON output
        link_pdf_map = {}

        # If links were found, display them in an embed
        if links_by_domain:
            mises_links = []
            library_lol_links = []
            empty_links = []

            for link in links_by_domain.get('mises.org', []):
                pdf_url = await PDFDownloader.get_pdf_url(link)
                if Utilities.is_empty(pdf_url):
                    empty_links.append(link)
                else:
                    mises_links.append(f"[Link]({link}) -> [PDF]({pdf_url})")
                    link_pdf_map[link] = pdf_url

            for link in links_by_domain.get('library.lol', []):
                pdf_url = await PDFDownloader.get_pdf_url(link)
                if Utilities.is_empty(pdf_url):
                    empty_links.append(link)
                else:
                    library_lol_links.append(f"[Link]({link}) -> [PDF]({pdf_url})")
                    link_pdf_map[link] = pdf_url

            # Save the results to a JSON file
            json_file_path = "link_pdf_map.json"
            with open(json_file_path, "w", encoding="utf-8") as json_file:
                json.dump(link_pdf_map, json_file, indent=4)

            await ctx.send(f"Links and PDF URLs have been saved to `{json_file_path}`")

            # Send the extracted PDF links for mises.org in batches
            if mises_links:
                for i in range(0, len(mises_links), 5):  # Batch size of 2
                    batch = mises_links[i:i + 5]
                    embed = discord.Embed(
                        title="Extracted PDF Links from mises.org",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Links", value="\n".join(batch), inline=False)
                    await ctx.send(embed=embed)

            # Send the extracted PDF links for library.lol in batches
            if library_lol_links:
                for i in range(0, len(library_lol_links), 2):  # Batch size of 1
                    batch = library_lol_links[i:i + 2]
                    embed = discord.Embed(
                        title="Downloaded PDF Links from library.lol",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Links", value="\n".join(batch), inline=False)
                    await ctx.send(embed=embed)

            # Send a summary of domains and link counts at the end
            summary_text = "\n".join(f"{domain}: {len(links)} links" for domain, links in links_by_domain.items())
            empty_links_text = f"Empty Links: \n" + "\n".join(f"{link}" for link in empty_links)
            summary_embed = discord.Embed(
                title=f"Summary of Links by Domain in {target_channel.name} \n",
                description=summary_text + "\n" + empty_links_text,
                color=discord.Color.green()
            )
            await ctx.send(embed=summary_embed)

        else:
            await ctx.send(f"No links found in {target_channel.mention}.")

async def setup(bot):
    await bot.add_cog(Commands(bot))