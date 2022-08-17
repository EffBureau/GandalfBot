from discord import FFmpegPCMAudio
import random
import os
from discord.ext import commands
import json
from dotenv import load_dotenv
from cogs.music import Music
from utils.utils import Utils
from utils.quotes import Quotes

load_dotenv("variables.env")

# Initiate bot
bot = commands.Bot(command_prefix="!")

Quotes.download_quotes()

"""Get all quotes in an array"""

quotes = []

with open('quotes.json') as json_quotes:
    quotes.extend(json.load(json_quotes))


@bot.event
async def on_ready():
    """When the bot is online"""
	
    print('We have logged in as {0.user}'.format(bot))

async def gandalf(message):
    """Plays a random gandalf quote whenever "gandalf" is present in message"""

    ctx = await bot.get_context(message)
    voice_client = message.guild.voice_client
    quote_to_play = quotes[random.randint(0, len(quotes) - 1)]
    player = FFmpegPCMAudio(os.path.join("quotes", quote_to_play), executable=os.environ.get("FFMPEG_PATH"))    

    if voice_client is not None:
        if voice_client.is_playing():
            await ctx.send("This feature isn't available while a song is playing")
        else:        
            Utils.play_audio(ctx, player)
            await Utils.let_bot_sleep(ctx)
    else:  
        await Utils.connect(ctx)
        Utils.play_audio(ctx, player)   
        await Utils.let_bot_sleep(ctx)

@bot.event
async def on_message(message):      
    """On message in chat"""
    
    if message.author is bot.user: # Making sure bot doesn't read own messages
        return

    if "gandalf" in message.content.lower():
        gandalf(message)
    
    await bot.process_commands(message) # This is needed to trigger actual commands like !play or !stop
            
bot.add_cog(Music(bot))
bot.add_cog(Utils(bot))
bot.run(os.environ.get("TOKEN"))