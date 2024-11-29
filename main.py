import asyncio
from dotenv import load_dotenv

from application_context import ApplicationContext
from discord_command_handler import Commands

load_dotenv()

context = ApplicationContext()
bot = context.bot


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def main():
    try:
        await bot.add_cog(Commands(bot, context))
        await bot.start(context.config.DISCORD_API_KEY)
    except (asyncio.CancelledError, KeyboardInterrupt):
        print("Bot is shutting down...")
    finally:
        await bot.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Program interrupted by user.")
