import discord
from discord import FFmpegPCMAudio, app_commands
import random
import os
from discord.ext import commands
import json
from dotenv import load_dotenv
from cogs.utils import utils
from utils.quotes import Quotes

load_dotenv(os.path.join(os.path.dirname(__file__), 'variables.env'))

class mybot(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix = "##",
            case_insensitive = True,
            intents = discord.Intents.all())
        
        self.dirname = os.path.dirname(__file__)
        self.quotes = []
        self.initial_extensions = [
            "cogs.music",
            "cogs.utils"
        ]

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)

        await bot.tree.sync()
    
    def load_quotes(self):
        """Get all quotes in an array"""
        
        Quotes.download_quotes()

        with open(os.path.join(self.dirname, 'quotes.json')) as json_quotes:
            self.quotes.extend(json.load(json_quotes))

    async def on_ready(self):
        """When the bot is online"""
        
        self.load_quotes()

        print('We have logged in as {0.user}'.format(self))

    async def gandalf(self, message):
        """Plays a random gandalf quote whenever "gandalf" is present in message"""

        ctx = await bot.get_context(message)
        voice_client = await utils.connect_message(ctx, self)
        quote_to_play = self.quotes[random.randint(0, len(self.quotes) - 1)]
        player = FFmpegPCMAudio(os.path.join(self.dirname,
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
            await ctx.send("Gandalf now works with slash commands! try /play")


        if "gandalf" in message.content.lower():
            await self.gandalf(message)

        # This is needed to trigger actual commands like !play or !stop
        await bot.process_commands(message)

bot = mybot()
bot.run(os.environ.get("TOKEN"))
