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
            return await ctx.author.voice.channel.connect()

        return ctx.message.guild.voice_client

    @classmethod
    async def let_bot_sleep(self, ctx):
        voice_client = ctx.message.guild.voice_client

        voice_client.pause() # Pause the client to let it set up the stream
        await asyncio.sleep(2) # Letting the bot sleep fixes an issue with the player going fast for the first couple of seconds
        voice_client.resume()
    
    # Source: https://stackoverflow.com/questions/63658589/how-to-make-a-discord-bot-leave-the-voice-channel-after-being-inactive-for-x-min
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global client         

        if not member.id == client.user.id:
            return

        elif before.channel is None: 
            voice = after.channel.guild.voice_client
            time = 0

            while True: # This while loop checks if the bot is playing audio
                await asyncio.sleep(1)
                time = time + 1
                if voice.is_playing() and not voice.is_paused(): # If it's playing or paused, reset timer
                    time = 0
                if time == 600: # If it gets to 10 minutes, disconnect
                    await voice.disconnect()
                if not voice.is_connected():
                    break