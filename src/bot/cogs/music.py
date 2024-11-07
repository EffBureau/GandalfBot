import asyncio
import datetime
import os
import time
import discord
from yt_dlp import YoutubeDL
from discord.ext import commands
from discord import app_commands
from cogs.utils import utils

class music(commands.Cog):
    """Contains methods used for playing sounds """
    queues = {}

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.dirname = os.path.dirname(__file__)

    async def play_audio(self, ctx, url):
        """"Plays audio from url"""
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        print(datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S") + " > " + "Now playing: " + player.title)
        await ctx.followup.send(f'Now playing: {player.title}')

        voice_client = await utils.connect_interaction(ctx)
        voice_client.play(player, after=lambda c: self.play_next(ctx))
        await utils.let_bot_sleep(ctx)

    def play_next(self, ctx):
        """"Plays next audio from queue"""
        server = ctx.guild
        voice_client = server.voice_client
        next_url = self.get_next_url(ctx)

        if next_url is not None:
            loop = self.bot.loop or asyncio.get_event_loop()

            next_player = asyncio.run_coroutine_threadsafe(self.get_player(ctx, next_url), loop)

            voice_client.play(next_player.result(), after=lambda c: self.play_next(ctx))
            asyncio.run_coroutine_threadsafe(utils.let_bot_sleep(ctx), loop)

    def get_next_url(self, ctx):
        """Gets next url in queue""" 
        server = ctx.guild

        if self.queues.get(server.id):
            return self.queues[server.id].pop(0)

    async def get_player(self, ctx, url):
        """Gets the player for specified url"""
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)

        await ctx.channel.send(f'Now playing: {player.title}')
        return player

    async def enqueue(self, ctx, url):
        """Appends url to queue"""
        server = ctx.guild

        if server.id in self.queues:
            self.queues[server.id].append(url)
        else:
            self.queues[server.id] = [url]

        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        await ctx.followup.send(player.title + " has been added to the queue. Position #" + str(len(self.queues[server.id])))

    async def play_stored_song(self, ctx, player, msg):
        """Plays song that is already stored on computer"""
        voice_client = await utils.connect_interaction(ctx)

        if voice_client is not None:
            if voice_client.is_playing():
                await ctx.response.send_message("This song cannot be added to the queue. Wait for all songs to finish playing.")
            else:
                voice_client.play(player)
                await utils.let_bot_sleep(ctx)

                await ctx.response.send_message(msg)
        else:
            await voice_client.play(player)

    @app_commands.command(name="play", description="Plays a video\'s audio using the specified youtube url")
    async def play(self, ctx: discord.Interaction, *, url: str):
        """Command that plays a video\'s audio using the specified youtube url"""
        print(datetime.datetime.now().strftime("%m-%d-%Y, %H:%M:%S") + " > " + "Url: " + url)

        voice_client = ctx.guild.voice_client
        await ctx.response.defer()

        if voice_client is not None:
            if voice_client.is_playing():
                await self.enqueue(ctx, url)
            else:
                await self.play_audio(ctx, url)
        else:
            await self.play_audio(ctx, url)

    @app_commands.command(name="clear", description="Clears the song queue")
    async def clear_queue(self, ctx: discord.Interaction):
        """Command that clears the song queue"""
        server = ctx.guild

        if server.id not in self.queues or self.queues[server.id] is []:
            await ctx.response.send_message("May the wind under your wings bear you where the sun sails and the moon walks.")
        else:
            self.queues[server.id] = []
            await ctx.response.send_message("Cleared queue")

    @app_commands.command(name="skip", description="Skips the current song")
    async def skip(self, ctx: discord.Interaction):
        """Command that skips the current song"""
        voice_client = ctx.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():
                voice_client.stop()

                await ctx.response.send_message("Skipped")
            else:
                await ctx.response.send_message("Nothing to skip")
        else :
            await ctx.response.send_message("Nothing to skip")

    @app_commands.command(name="stop", description="Stops the player")
    async def stop(self, ctx: discord.Interaction):
        """Stops the player"""
        voice_client = ctx.guild.voice_client
        server = ctx.guild

        if voice_client is not None:
            if voice_client.is_playing():
                self.queues[server.id] = []
                voice_client.stop()

                await ctx.response.send_message("Be silent. Keep your forked tongue behind your teeth. I have not passed through fire and death to bandy crooked words with a witless worm.")
            else:
                await ctx.response.send_message("Nothing to stop")
        else :
            await ctx.response.send_message("Nothing to stop")

    @app_commands.command(name="pause", description="Pauses the player")
    async def pause(self, ctx: discord.Interaction):
        """Command that pauses the player"""
        voice_client = ctx.guild.voice_client

        if voice_client is not None:
            if voice_client.is_playing():
                voice_client.pause()

                await ctx.response.send_message("I must rest here a moment, even if all the orcs ever spawned are after us.")
            else:
                await ctx.response.send_message("Nothing to pause")
        else :
            await ctx.response.send_message("Nothing to pause")

    @app_commands.command(name="resume", description="Resumes the player")
    async def resume(self, ctx: discord.Interaction):
        """Command that resumes the player"""
        voice_client = ctx.guild.voice_client

        if voice_client is not None:
            if voice_client.is_paused():
                voice_client.resume()

                await ctx.response.send_message("True Courage Is Knowing Not When To Take A Life, But When To Spare One.")
            else:
                await ctx.response.send_message("Nothing to resume")
        else :
            await ctx.response.send_message("Nothing to resume")

    @app_commands.command(name="jc", description="Plays the John Cena Intro")
    async def jc(self, ctx: discord.Interaction):
        """Command that plays the John Cena Intro"""
        player = discord.FFmpegPCMAudio((os.path.join(self.dirname, "../../songs/JohnCena.mp3")))

        await self.play_stored_song(ctx, player, "Now playing: John Cena")

    @app_commands.command(name="cantina", description="Plays the Star Wars Cantina")
    async def cantina(self, ctx: discord.Interaction):
        """Command that plays the Star Wars Cantina"""
        player = discord.FFmpegPCMAudio(os.path.join(self.dirname, "../../songs/Cantina.mp3"))

        await self.play_stored_song(ctx, player, "Now playing: Cantina")

    @app_commands.command(name="lw", description="Plays Lost Woods from Zelda: Ocarina of Time")
    async def lw(self, ctx: discord.Interaction):
        """Command that plays Lost Woods from Zelda: Ocarina of Time"""
        player = discord.FFmpegPCMAudio((os.path.join(self.dirname, "../../songs/LostWoods.mp3")))

        await self.play_stored_song(ctx, player, "Now playing: Lost Woods")

    @app_commands.command(name="lqgr", description="Plays lqgr song-oh my god!")
    async def lqgr(self, ctx: discord.Interaction):
        """Command that plays lqgr song"""
        player = discord.FFmpegPCMAudio((os.path.join(self.dirname, "../../songs/Lqgr.mp3")))

        await self.play_stored_song(ctx, player, "Now playing: lqgr song-oh my god!")

    @app_commands.command(name="fb", description="Plays a Free Bird soundbyte!")
    async def fb(self, ctx: discord.Interaction):
        """Command that plays a Free Bird soundbyte"""
        player = discord.FFmpegPCMAudio((os.path.join(self.dirname, "../../songs/freebird.mp3")))

        await self.play_stored_song(ctx, player, "Now playing: Free Bird soundbyte!")

async def setup(bot: commands.Bot) -> None:
    """Adds cog to bot"""
    await bot.add_cog(music(bot))

# Source for some of the code below: https://github.com/Rapptz/discord.py/blob/45d498c1b76deaf3b394d17ccf56112fa691d160/examples/basic_voice.py
ytdl_format_options = {
    'compat_opts': {'format-sort'},
    'format_sort': ['hasaud',
                 'lang',
                 'quality',
                 'tbr',
                 'filesize',
                 'vbr',
                 'height',
                 'width',
                 'proto',
                 'vext',
                 'abr',
                 'aext',
                 'fps',
                 'fs_approx',
                 'source',
                 'id'],
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
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

ytdl = YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    """YTDL util class for extracting audio from url"""
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """Extracts youtube player from url"""
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
