from asyncio.windows_events import NULL
import discord
from discord import FFmpegPCMAudio
import random
import glob, os
from bs4 import BeautifulSoup
import requests
from discord.ext import commands
import json
import yt_dlp
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

voice = None

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
  global voice

  if not (is_connected(ctx)):
    voice = await ctx.author.voice.channel.connect()

# Plays a random quote
async def play_audio(source):  
  if voice.is_playing():
    voice.stop()

  voice.play(source)

# Downloads youtube video from url using yt-dlp
async def download_yt_video_from_url(url):
  ydl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': 192,
    }]
  }

  with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ydl.download([url])

async def rename_song_file():
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")

# On message in chat
@bot.event
async def on_message(message):      

  # Making sure bot doesn't read own messages
  if message.author is bot.user:
      return

  global voice

  if "gandalf" in message.content:
    await connect(message)
    
    source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))
    await play_audio(source)

  # This is needed to trigger actual commands like !play or !stop
  await bot.process_commands(message)

# Checks if a song is already playing
async def is_song_there() -> bool:
  for file in os.listdir("./"):
    if file.title() == "Song.Mp3":
      return True
  
  return False

@bot.command(brief='Plays a video\'s audio using youtube URL specified')
async def play(ctx, arg):
  if voice is None:
    await play_song(ctx, arg)
  else: 
    if not voice.is_playing():
      await play_song(ctx, arg)
    else: 
      # Add song to queue
      await ctx.send("Queues haven't been implemented yet. Please use !stop or wait until song has finished playing")

async def play_song(ctx, arg):
  song_there = await is_song_there()

  if song_there:
    os.remove("song.mp3")
  
  await connect(ctx)

  await download_yt_video_from_url(arg)
  await rename_song_file()

  source = discord.FFmpegPCMAudio("song.mp3")
  await play_audio(source)
  
@bot.command(brief='Stops the player')
async def stop(ctx):
  global voice

  if voice is not None:
    if voice.is_playing():
      voice.stop()

@bot.command(brief='Pauses the player')
async def pause(ctx):
  global voice

  if voice is not None:
    if voice.is_playing():
      voice.pause()

@bot.command(brief='Resumes the player')
async def resume(ctx):
  global voice

  if voice is not None:
    if voice.is_paused():
      voice.resume()

@bot.command(brief='Plays the John Cena Intro')
async def jc(ctx):
    await connect(ctx)

    source = discord.FFmpegPCMAudio("songs/JohnCena.mp3")
    await play_audio(source)

@bot.command(brief='Plays the Star Wars Cantina')
async def cantina(ctx):
    await connect(ctx)

    source = discord.FFmpegPCMAudio("songs/Cantina.mp3")
    await play_audio(source)


bot.run(os.environ.get("TOKEN"))