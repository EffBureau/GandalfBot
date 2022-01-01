from asyncio.windows_events import NULL
from gc import get_stats
import discord
from discord import FFmpegPCMAudio
import random
import glob, os
from bs4 import BeautifulSoup
from discord.errors import ClientException
from discord.voice_client import VoiceClient
import requests
from requests.structures import CaseInsensitiveDict
from discord.ext.commands import Bot
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

# Get all quotes in an array
quotes = []

voice = None

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
async def playAudio(source):  
  if voice.is_playing():
    voice.stop()

  voice.play(source)

async def downloadVideoFromYtUrl(url):
  ydl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': 192,
    }]
  }

  with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ## ajouter variable isDownloading
    ydl.download([url])

async def renameSongFile():
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")

# On message in chat
@bot.event
async def on_message(message):      

  # Making sure bot doesn't read own messages
  if message.author == bot.user:
      return

  global voice

  if "gandalf" in message.content:
    await connect(message)
    
    source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))
    await playAudio(source)

  # This is needed to trigger Commands like !playAudio or !stop
  await bot.process_commands(message)

# Checks if a song is already playing
async def isSongThere() -> bool:
  for file in os.listdir("./"):
    if file.title() == "Song.Mp3":
      return True
  
  return False

# Plays a song using youtube URL specified
@bot.command()
async def play(ctx, arg):
  if voice == None:
    await play_song(ctx, arg)
  else: 
    if not voice.is_playing():
      await play_song(ctx, arg)
    else: 
      # Add song to queue
      ctx.send("Queues haven't been implemented yet. Please use !stop or wait until song has finished playing")

async def play_song(ctx, arg):
  song_there = await isSongThere()

  if song_there:
    os.remove("song.mp3")
  
    await connect(ctx)

    await downloadVideoFromYtUrl(arg)  
    await renameSongFile()

    source = discord.FFmpegPCMAudio("song.mp3")
    await playAudio(source)
  

  

@bot.command()
async def stop(ctx):
  if is_connected(ctx):
    global voice

    voice.stop()

bot.run(os.environ.get("TOKEN"))