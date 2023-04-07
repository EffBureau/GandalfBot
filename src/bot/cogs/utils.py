import asyncio
import discord
from discord.ext import commands

class utils(commands.Cog):
    """
        Contains useful methods for checking connection,
        connecting to a voice channel or disconnecting.
    """
    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def is_connected_message(cls, ctx, client):
        """Checks if bot is connected to voice channel"""
        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        is_connected = voice_client and voice_client.is_connected()

        return is_connected

    @classmethod
    async def connect_message(cls, ctx, client):
        """"Connects to a voice channel"""
        if not cls.is_connected_message(ctx, client):
            print("Connected to : " + ctx.guild.name)
            return await ctx.author.voice.channel.connect()

        return ctx.message.guild.voice_client

    @classmethod
    def is_connected_interaction(cls, ctx):
        """Checks if bot is connected to voice channel"""
        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        is_connected = voice_client and voice_client.is_connected()

        return is_connected

    @classmethod
    async def connect_interaction(cls, ctx):
        """"Connects to a voice channel"""
        if not cls.is_connected_interaction(ctx):
            print("Connected to : " + ctx.guild.name)
            return await ctx.user.voice.channel.connect()

        ctx.response.defer()
        
        return ctx.guild.voice_client

    @classmethod
    async def let_bot_sleep(cls, ctx):
        """
            Lets the bot sleep for a while. 

            Used to fix an issue where the bot 
            would go faster in the first couple of seconds.
        """
        voice_client = ctx.guild.voice_client

        voice_client.pause() # Pause the client to let it set up the stream
        await asyncio.sleep(2) # Letting the bot sleep fixes an issue with the player going fast for the first couple of seconds
        voice_client.resume()

    # Source: https://stackoverflow.com/questions/63658589/how-to-make-a-discord-bot-leave-the-voice-channel-after-being-inactive-for-x-min
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        """Handles the idle timer after which the bot disconnects"""
        if not member.id == self.bot.user.id:
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
    # End source

async def setup(bot: commands.Bot) -> None:
    """Adds cog to bot"""
    await bot.add_cog(utils(bot))
