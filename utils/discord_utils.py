import asyncio
import re
import json
import discord
from discord import message
from discord.ext import commands
import urllib.parse
from urllib.parse import urlparse


class DiscordUtils:

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
    async def wait_for_user_response(ctx, prompt: str = "", timeout=30, update_interval=1):
        """
        Prompts the user in a Discord channel and waits for their response, showing a loading bar.

        :param ctx: The context of the command.
        :param prompt: The message to prompt the user with.
        :param timeout: The time in seconds to wait for a response (default: 30).
        :param update_interval: The time interval (in seconds) to update the loading bar (default: 1).
        :return: True if the user responded, False if the timeout elapsed.
        """
        # Full loading bar representation
        full_bar = "####################"  # 20 '#' characters for 100%
        bar_length = len(full_bar)

        # Send the initial prompt message with the loading bar
        loading_message = await ctx.send(f"{prompt}\n`[{full_bar[:0].ljust(bar_length)}] 0%`")

        def check(msg):
            # Ensure the response is from the command invoker in the same channel
            return msg.author == ctx.author and msg.channel == ctx.channel

        elapsed_time = 0
        try:
            while elapsed_time < timeout:
                try:
                    # Wait for a message from the user within the update interval
                    response = await ctx.bot.wait_for('message', timeout=update_interval, check=check)
                    # User responded within the timeout
                    return response.content.strip()
                except asyncio.TimeoutError:
                    # Update the elapsed time and loading bar
                    elapsed_time += update_interval
                    progress = int((elapsed_time / timeout) * bar_length)
                    percentage = int((elapsed_time / timeout) * 100)
                    bar_display = f"`[{full_bar[:progress].ljust(bar_length)}] {percentage}%`"
                    await loading_message.edit(content=f"{prompt}\n{bar_display}")

            # Timeout reached, no response
            return None
        except Exception as e:
            # Handle unexpected errors
            await ctx.send(f"An error occurred: {str(e)}")
            return None

    @staticmethod
    async def confirm_and_run(bot, channel_id, user_id, func, prompt, *args, **kwargs):
        """
        Prompts the user in a Discord channel to confirm before running the specified function.

        :param bot: The Discord bot instance.
        :param channel_id: The ID of the Discord channel to send the prompt to.
        :param user_id: The ID of the user who needs to confirm.
        :param func: The function to run if confirmed.
        :param prompt: The prompt message displayed in the Discord channel.
        :param args: Positional arguments for the function.
        :param kwargs: Keyword arguments for the function.
        """
        # Fetch the channel and user
        channel = bot.get_channel(channel_id)
        if not channel:
            raise ValueError("Invalid channel ID. The channel could not be found.")

        user = await bot.fetch_user(user_id)
        if not user:
            raise ValueError("Invalid user ID. The user could not be found.")

        # Send the initial prompt message with the loading bar
        loading_message = await channel.send(f"{prompt} (Y/N):\n`[                    ] 0%`")
        loading_bar = "####################"  # Full loading bar for 100%
        timeout = 30  # Timeout in seconds
        interval = 1.5  # Update interval for the loading bar
        elapsed_time = 0

        def check(msg):
            # Check that the message is from the specified user and in the same channel
            return (
                    msg.author.id == user_id and
                    msg.channel.id == channel_id and
                    msg.content.strip().upper() in ['Y', 'N', 'y', 'n']
            )

        while elapsed_time < timeout:
            try:
                # Wait for a response from the user with the specified timeout
                response = await bot.wait_for('message', timeout=interval, check=check)
                user_response = response.content.strip().upper()

                if user_response == 'Y' or user_response == 'y':
                    # Confirm and execute the function
                    if asyncio.iscoroutinefunction(func):
                        await func(*args, **kwargs)
                    else:
                        func(*args, **kwargs)
                    return True
                elif user_response == 'N' or user_response == 'n':
                    # User declined
                    return False
                else:
                    await channel.send("Invalid input. Please enter 'Y' or 'N'.")
                    return await DiscordUtils.confirm_and_run(func, prompt, *args, **kwargs)
            except asyncio.TimeoutError:
                # Update the loading bar in the message
                elapsed_time += interval
                progress = int((elapsed_time / timeout) * 20)  # 20 slots in the loading bar
                bar_display = f"`[{loading_bar[:progress].ljust(20)}] {int((elapsed_time / timeout) * 100)}%`"
                await loading_message.edit(content=f"{prompt} (Y/N):\n{bar_display}")

        # Timeout handling
        await channel.send("No response received. Action timed out.")
        return False
