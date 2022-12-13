import discord
import asyncio
from discord.ext import commands

class utils(commands.Cog):    

    def __init__(self, bot):
        self.bot = bot

    @classmethod
    def is_connected_message(self, ctx, client):
        """Checks if bot is connected to voice channel"""

        voice_client = discord.utils.get(client.voice_clients, guild=ctx.guild)
        isConnected = voice_client and voice_client.is_connected()

        return isConnected

    @classmethod
    async def connect_message(self, ctx, client):
        """"Connects to a voice channel"""

        if not self.is_connected_message(ctx, client):
            print("Connected to : " + ctx.guild.name)            
            return await ctx.author.voice.channel.connect()

        return ctx.message.guild.voice_client

    @classmethod
    def is_connected_interaction(self, ctx):
        """Checks if bot is connected to voice channel"""

        voice_client = discord.utils.get(ctx.client.voice_clients, guild=ctx.guild)
        isConnected = voice_client and voice_client.is_connected()

        return isConnected

    @classmethod
    async def connect_interaction(self, ctx):
        """"Connects to a voice channel"""

        if not self.is_connected_interaction(ctx):
            print("Connected to : " + ctx.guild.name)
            return await ctx.user.voice.channel.connect()

        return ctx.guild.voice_client

    @classmethod
    async def let_bot_sleep(self, ctx):
        voice_client = ctx.guild.voice_client

        voice_client.pause() # Pause the client to let it set up the stream
        await asyncio.sleep(2) # Letting the bot sleep fixes an issue with the player going fast for the first couple of seconds
        voice_client.resume()

    @classmethod
    def get_url_type(self, url):
        """ Returns the playlist url type """

        # Url is of a specific video in a playlist
        if 'watch?v=' in url and '&list=' in url:
            return 1
        # Url is an actual playlist
        elif 'playlist?list=' in url:
            return 2 
        
        # Url is a single video
        return 0

    @classmethod    
    def get_video_url(self, url):
        """Gets the video url in given playlist url"""

        if 'watch?v=' in url and '&list=' in url:
            # Sample url : https://www.youtube.com/watch?v=RS2u4_AJdTA&list=PL1Xdrt_TmtOT9ze2-7U20SwPUSMWStefq&index=3
            return str(url.split('/watch?v=')[1].split('&list='))
    
    # Source: https://stackoverflow.com/questions/63658589/how-to-make-a-discord-bot-leave-the-voice-channel-after-being-inactive-for-x-min
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):   
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
    await bot.add_cog(utils(bot))