import asyncio
from discord.ext import commands
from asyncio.windows_events import NULL
import discord
from discord import FFmpegPCMAudio
from discord.ext import commands
import youtube_dl

from utils.utils import Utils



# Source for some of the code below: https://github.com/Rapptz/discord.py/blob/45d498c1b76deaf3b394d17ccf56112fa691d160/examples/basic_voice.py
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)


        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class Music(commands.Cog):
    queues = {}

    def __init__(self, bot):
        self.bot = bot

    @classmethod    
    def play_audio(self, ctx, player):
        """"Plays audio from player"""

        voice_client = ctx.message.guild.voice_client
        voice_client.play(player, after=lambda c: self.get_next_player(ctx))

    @classmethod
    def get_next_player(self, ctx):        
        server = ctx.message.guild

        if self.queues[server.id] != []:
            player = self.queues[server.id].pop(0)
            self.play_audio(ctx, player)

    async def stream_audio(self, ctx, player):
        async with ctx.typing():
            await Utils.connect(ctx)   
            self.play_audio(ctx, player)
            await Utils.let_bot_sleep(ctx)

    
        await ctx.send(f'Now playing: {player.title}')

    async def enqueue(self, ctx, player):
        server = ctx.message.guild

        if server.id in self.queues:
            self.queues[server.id].append(player)
        else:
            self.queues[server.id] = [player]

        if type(player) is not FFmpegPCMAudio:      
            await ctx.send(player.title + " has been added to the queue. Position #" + str(len(self.queues[server.id])))

    @commands.command(brief='Plays a video\'s audio using youtube URL specified')
    async def play(self, ctx, *, url):
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():        
                await self.enqueue(ctx, player)
            else:
                await self.stream_audio(ctx, player)
        else:  
            await self.stream_audio(ctx, player)

    @commands.command(brief='Clears the queue')
    async def clear(self, ctx):
        server = ctx.message.guild

        if server.id not in self.queues or self.queues[server.id] is []:
            await ctx.send("The queue is empty")
        else:
            self.queues[server.id] = []
            await ctx.send("Cleared queue")

    @commands.command(brief='Skips the current song')
    async def skip(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():  
                voice_client.stop()              
                await ctx.send("Skipped")
            else:
                await ctx.send("Nothing to skip")
        else :
            await ctx.send("Nothing to skip")
    

    @commands.command(brief='Stops the player')
    async def stop(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():  
                voice_client.stop()

                await ctx.send("Stopping")
            else:
                await ctx.send("Nothing to stop")
        else :
            await ctx.send("Nothing to stop")

    @commands.command(brief='Pauses the player')
    async def pause(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():  
                voice_client.pause()
        
                await ctx.send("Pausing")
            else:
                await ctx.send("Nothing to pause")
        else :
            await ctx.send("Nothing to pause")

    @commands.command(brief='Resumes the player')
    async def resume(self, ctx):
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():        
                voice_client.resume()

                await ctx.send("Resuming")
            else:
                await ctx.send("Nothing to resume")
        else :
            await ctx.send("Nothing to resume")

    @commands.command(brief='Plays the John Cena Intro')
    async def jc(self, ctx):
        player = discord.FFmpegPCMAudio("../songs/JohnCena.mp3")
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():       
                await ctx.send("This song cannot be added to the queue. Wait for all songs to finish playing.")
            else:
                self.play_audio(ctx, player)
                await Utils.let_bot_sleep(ctx)

                await ctx.send("Now playing: John Cena")
        else:  
            await Utils.connect(ctx)
            self.play_audio(ctx, player)
            await Utils.let_bot_sleep(ctx)
      
            await ctx.send("Now playing: John Cena")

    @commands.command(brief='Plays the Star Wars Cantina')
    async def cantina(self, ctx):
        player = discord.FFmpegPCMAudio("../songs/Cantina.mp3")
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():                
                await ctx.send("This song cannot be added to the queue. Wait for all songs to finish playing.")
            else:
                self.play_audio(ctx, player)
                await Utils.let_bot_sleep(ctx)

                await ctx.send("Now playing: Cantina")
        else:  
            await Utils.connect(ctx)
            self.play_audio(ctx, player)
            await Utils.let_bot_sleep(ctx)

            await ctx.send("Now playing: Cantina")

    @commands.command(brief='Plays Lost Woods from Zelda: Ocarina of Time')
    async def lw(self, ctx):
        player = discord.FFmpegPCMAudio("../songs/LostWoods.mp3")
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():       
                await ctx.send("This song cannot be added to the queue. Wait for all songs to finish playing.")
            else:
                self.play_audio(ctx, player)
                await Utils.let_bot_sleep(ctx)

                await ctx.send("Now playing: Lost woods")
        else:  
            await Utils.connect(ctx)
            self.play_audio(ctx, player)
            await Utils.let_bot_sleep(ctx)

            await ctx.send("Now playing: Lost woods")