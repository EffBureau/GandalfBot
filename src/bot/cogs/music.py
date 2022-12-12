import asyncio
import discord
import youtube_dl
from discord.ext import commands
from discord import FFmpegPCMAudio
from utils.utils import Utils

class music(commands.Cog):

    queues = {}

    def __init__(self, bot):
        self.bot = bot
    
    async def play_audio(self, ctx, url):
        """"Plays audio from url"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
        await ctx.send(f'Now playing: {player.title}')

        voice_client = await Utils.connect(ctx)
        voice_client.play(player, after=lambda c: self.play_next(ctx))
        await Utils.let_bot_sleep(ctx)

    def play_next(self, ctx):
        """"Plays next audio from queue"""

        server = ctx.message.guild
        voice_client = server.voice_client
        
        next_url = self.get_next_url(ctx)

        if next_url is not None:
            loop = self.bot.loop or asyncio.get_event_loop()

            next_player = asyncio.run_coroutine_threadsafe(self.get_player(ctx, next_url), loop)

            voice_client.play(next_player.result(), after=lambda c: self.play_next(ctx))
            asyncio.run_coroutine_threadsafe(Utils.let_bot_sleep(ctx), loop)

    def get_next_url(self, ctx):    
        """Gets next url in queue""" 

        server = ctx.message.guild
        
        if self.queues[server.id]:
            return self.queues[server.id].pop(0)    
    
    async def get_player(self, ctx, url):
        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            
        await ctx.send(f'Now playing: {player.title}')
        return player

    async def enqueue(self, ctx, url):
        """Appends url to queue"""

        server = ctx.message.guild

        if server.id in self.queues:
            self.queues[server.id].append(url)
        else:
            self.queues[server.id] = [url]

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)    
        await ctx.send(player.title + " has been added to the queue. Position #" + str(len(self.queues[server.id])))

    async def play_stored_song(self, ctx, player, msg):
        """Plays song that is already stored on computer"""

        voice_client = await Utils.connect(ctx)

        if voice_client is not None:
            if voice_client.is_playing():       
                await ctx.send("This song cannot be added to the queue. Wait for all songs to finish playing.")
            else:
                voice_client.play(player)
                await Utils.let_bot_sleep(ctx)

                await ctx.send(msg)

    @commands.command(brief='Plays a video\'s audio using youtube URL specified')
    async def play(self, ctx, *, url):        
        voice_client = ctx.message.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():        
                await self.enqueue(ctx, url)
            else:
                await self.play_audio(ctx, url)
        else:  
            await self.play_audio(ctx, url)

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
        server = ctx.message.guild

        if voice_client is not None:
            if voice_client.is_playing():  
                self.queues[server.id] = []
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

        await self.play_stored_song(ctx, player, "Now playing: John Cena")

    @commands.command(brief='Plays the Star Wars Cantina')
    async def cantina(self, ctx):
        player = discord.FFmpegPCMAudio("../songs/Cantina.mp3")        

        await self.play_stored_song(ctx, player, "Now playing: Cantina")

    @commands.command(brief='Plays Lost Woods from Zelda: Ocarina of Time')
    async def lw(self, ctx):
        player = discord.FFmpegPCMAudio("../songs/LostWoods.mp3")
        
        await self.play_stored_song(ctx, player, "Now playing: Lost Woods")

