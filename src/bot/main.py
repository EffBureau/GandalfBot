"""This is the main module for Gandalf bot"""
import logging
import datetime
import random
import os
import json
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs.utils import utils
from utils.quotes import quotes

load_dotenv(os.path.join(os.path.dirname(__file__), 'variables.env'))

class mybot(commands.Bot):
    """Contains the main methods for Gandalf bot"""
    def __init__(self):
        super().__init__(
            command_prefix = "##",
            case_insensitive = True,
            intents = discord.Intents.all())    

        self.dirname = os.path.dirname(__file__)
        self.quotes = []
        self.initial_extensions = [
            "cogs.music",
            "cogs.utils",
            "cogs.translate",
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await bot.tree.sync()

    def load_quotes(self):
        """Get all quotes in an array"""
        quotes.download_quotes()

        with open(os.path.join(self.dirname, 'quotes.json'), encoding='utf-8') as json_quotes:
            self.quotes.extend(json.load(json_quotes))

    async def on_ready(self):
        """When the bot is online"""
        self.load_quotes()

        print(datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S") + " > " + 'We have logged in as {0.user}'.format(self))

    async def gandalf(self, message):
        """Plays a random gandalf quote whenever "gandalf" is present in message"""
        ctx = await bot.get_context(message)
        voice_client = await utils.connect_message(ctx, self)
        quote_to_play = self.quotes[random.randint(0, len(self.quotes) - 1)]
        player = discord.FFmpegPCMAudio(os.path.join(self.dirname,
            "../quotes", quote_to_play), executable=os.environ.get("FFMPEG_PATH"))

        if voice_client is not None:
            if voice_client.is_playing():
                await ctx.send("This feature isn't available while a song is playing")
            else:
                voice_client.play(player)
                await utils.let_bot_sleep(ctx)

    async def on_message(self, message):
        """On message in chat"""
        if message.author.id is bot.user.id:  # Making sure bot doesn't read own messages
            return

        if  '!play' in message.content.lower():
            ctx = await bot.get_context(message)
            await ctx.send("Gandalf now works with slash commands! Try /play")

        if "gandalf" in message.content.lower():
            await self.gandalf(message)

        # This is needed to trigger actual commands like /play or /stop
        await bot.process_commands(message)

# Assume client refers to a discord.Client subclass...
bot = mybot()
date = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
handler = logging.FileHandler(filename='logs/discord-' + date + '.log', encoding='utf-8', mode='w')
bot.run(os.environ.get("TOKEN"), log_handler=handler, log_level=logging.DEBUG)
