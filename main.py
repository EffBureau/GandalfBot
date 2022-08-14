from asyncio.windows_events import NULL
import discord
from discord import FFmpegPCMAudio
import random
import glob, os
import asyncio
from bs4 import BeautifulSoup
import requests
from discord.ext import commands
import json
import youtube_dl
from dotenv import load_dotenv
load_dotenv("variables.env")

#######################################################################
## Download Gandalf Quotes
#######################################################################

# Find all .wav files
files = glob.glob("quotes/*.wav")

# Check if files are empty
if not any(files):

  # Page content
  url = "http://www.theargonath.cc/characters/gandalf/sounds/sounds.html"
  page = requests.get(url, allow_redirects=True)
  
  filenames = []
  soup = BeautifulSoup(page.content, "html.parser")

  # For each file to download
  for a_href in soup.find_all("a", href=True):
    if "html" not in a_href["href"]:
      r =  requests.get(a_href["href"], allow_redirects=True)

      # Split the link to get file name
      split_link = a_href["href"].split('/')
      quote = split_link[len(split_link) - 1]

      # Create file
      open(os.path.join("quotes", quote), 'wb').write(r.content)
      filenames.append(quote)
  
  # Dump all file names in a .json file
  with open('quotes.json', 'w') as outfile:
      json.dump(filenames, outfile)

#######################################################################
##*******************************************************************##
#######################################################################

#######################################################################
## Play sound files
#######################################################################

# Initiate bot
bot = commands.Bot(command_prefix="!")

# Get all quotes in an array
quotes = []

with open('quotes.json') as json_quotes:
  quotes.extend(json.load(json_quotes))

# When the bot is online
@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

# Checks if bot is connected to voice channel
def is_connected(ctx):
    voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    isConnected = voice_client and voice_client.is_connected() 
    return isConnected

# Connects to a voice channel
async def connect(ctx):
  if not (is_connected(ctx)):
    await ctx.author.voice.channel.connect()

# Plays audio from player
async def play_audio(ctx, player):
  if ctx.voice_client.is_playing():
    ctx.voice_client.stop()

  ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

  ctx.voice_client.pause() # Pause the client to let it set up the stream
  await asyncio.sleep(2)
  ctx.voice_client.resume()

# On message in chat
@bot.event
async def on_message(message):      

  # Making sure bot doesn't read own messages
  if message.author is bot.user:
      return

  # Plays a random gandalf quote whenever "gandalf" is present in message
  if "gandalf" in message.content.lower():
    ctx = await bot.get_context(message)
    await connect(ctx)
    
    source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))    
    await play_audio(ctx, source)

  # This is needed to trigger actual commands like !play or !stop
  await bot.process_commands(message)

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
  def __init__(self, bot):
    self.bot = bot

  async def stream_audio(self, ctx, url):
    await connect(ctx)
    async with ctx.typing():
      player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
      await play_audio(ctx, player)
    
    await ctx.send(f'Now playing: {player.title}')

  @commands.command(brief='Plays a video\'s audio using youtube URL specified')
  async def play(self, ctx, *, url):
    if ctx.voice_client is None:
      await self.stream_audio(ctx, url)
    else: 
      if not ctx.voice_client.is_playing():
        await self.stream_audio(ctx, url)
      else: 
        # Add song to queue
        await ctx.send("Queues haven't been implemented yet. Please use !stop or wait until song has finished playing")

  @commands.command(brief='Stops the player')
  async def stop(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_playing():
        ctx.voice_client.stop()

  @commands.command(brief='Pauses the player')
  async def pause(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_playing():
        ctx.voice_client.pause()

  @commands.command(brief='Resumes the player')
  async def resume(self, ctx):
    if ctx.voice_client is not None:
      if ctx.voice_client.is_paused():
        ctx.voice_client.resume()

  @commands.command(brief='Plays the John Cena Intro')
  async def jc(self, ctx):
      await connect(ctx)

      player = discord.FFmpegPCMAudio("songs/JohnCena.mp3")
      await play_audio(ctx, player)

  @commands.command(brief='Plays the Star Wars Cantina')
  async def cantina(self, ctx):
      await connect(ctx)

      player = discord.FFmpegPCMAudio("songs/Cantina.mp3")
      await play_audio(ctx, player)

  @commands.command(brief='Plays Lost Woods from Zelda: Ocarina of Time')
  async def lw(self, ctx):
      await connect(ctx)

      player = discord.FFmpegPCMAudio("songs/LostWoods.mp3")
      await play_audio(ctx, player)

bot.add_cog(Music(bot))
bot.run(os.environ.get("TOKEN"))