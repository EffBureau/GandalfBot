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

# Get all quotes in an arrat
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
    return voice_client and voice_client.is_connected()

# Connects to a voice channel
async def connect(ctx):
  global voice

  if not (is_connected(ctx)):
    voice = await ctx.author.voice.channel.connect()

voice = None

# Plays a random quote
async def playQuote():
  source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))
  try: 
   voice.play(source)
  except ClientException as e:

    # ClientException means audio is already playing
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
    connect(message)
    
    await playQuote()

  # This is needed to trigger Commands like !play or !stop
  await bot.process_commands(message)

# Checks if a song is already playing
async def isSongPlaying() -> bool:
  for file in os.listdir("./"):
    if file.title() == "Song.Mp3":
      return True
  
  return False

# Plays a song using youtube URL specified
@bot.command()
async def play(ctx, arg):
  song_playing = await isSongPlaying()
  
  global voice
  
  try:
    if song_playing:
      os.remove("song.mp3")
  except PermissionError as e:
    await ctx.send("Fly, you fools! (song already playing)")
  
  connect(ctx)

  downloadVideoFromYtUrl(url)
  
  renameSongFile()
  
  # Play file audio
  voice.play(discord.FFmpegPCMAudio("song.mp3"))

@bot.command()
async def stop(ctx):
  if is_connected():
    global voice

    voice.stop()


bot.run(os.environ.get("TOKEN"))