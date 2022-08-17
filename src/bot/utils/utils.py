import discord
import asyncio
from discord.ext import commands

class Utils(commands.Cog):    

    global client

    def __init__(self, bot):
        global client

        client = bot

    @classmethod
    def is_connected(self, ctx):
        """Checks if bot is connected to voice channel"""
        global client

        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        isConnected = voice_client and voice_client.is_connected()
        return isConnected

    @classmethod
    async def connect(self, ctx):
        """"Connects to a voice channel"""

        if not self.is_connected(ctx):
            await ctx.author.voice.channel.connect()

    @classmethod
    async def let_bot_sleep(self, ctx):
        voice_client = ctx.message.guild.voice_client

        voice_client.pause() # Pause the client to let it set up the stream
        await asyncio.sleep(2) # Letting the bot sleep fixes an issue with the player going fast for the first couple of seconds
        voice_client.resume()