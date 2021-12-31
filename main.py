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
## Download sound files
#######################################################################
#files = glob.glob("*.wav")
#for file in files:
#  os.remove(file)
#url = "http://www.theargonath.cc/characters/gandalf/sounds/sounds.html"
#page = requests.get(url, allow_redirects=True)
#
#filenames = []
#soup = BeautifulSoup(page.content, "html.parser")
#for a_href in soup.find_all("a", href=True):
#  if "html" not in a_href["href"]:
#    r =  requests.get(a_href["href"], allow_redirects=True)
#    split_link = a_href["href"].split('/')
#    quote = split_link[len(split_link) - 1]
#    open(os.path.join("quotes", quote), 'wb').write(r.content) 
#    filenames.append(quote)
#
#with open('quotes.json', 'w') as outfile:
#    json.dump(filenames, outfile)
#######################################################################
##*******************************************************************##
#######################################################################

#######################################################################
## Play sound files
#######################################################################
bot = commands.Bot(command_prefix="!")

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Authorization"] = "Bearer JQ6KMVxKnmWdTxYZYax3"

quotes = []

with open('quotes.json') as json_quotes:
  quotes.extend(json.load(json_quotes))

@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))

def is_connected(ctx):
    voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
    return voice_client and voice_client.is_connected()

voice = None

isPlaying = False

async def playQuote():
  source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))
  try: 
   voice.play(source)
  except ClientException as e:
    voice.stop()
    voice.play(source)



@bot.event
async def on_message(message):      

  if message.author == bot.user:
      return

  global voice

  if "gandalf" in message.content:
    voice_client = discord.utils.get(bot.voice_clients, guild=message.guild)
    
    if not (voice_client and voice_client.is_connected()):
      voice = await message.author.voice.channel.connect()
    
    await playQuote()

  await bot.process_commands(message)

async def isSongThere() -> bool:
  for file in os.listdir("./"):
    if file.title() == "Song.Mp3":
      return True
  
  return False

@bot.command()
async def play(ctx, arg):
  song_there = await isSongThere()
  
  global voice
  try:
    if song_there:
      os.remove("song.mp3")
  except PermissionError as e:
    await ctx.send("Fly, you fools! (song already playing)")

  voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  
  if not (voice_client and voice_client.is_connected()):
    voice = await ctx.author.voice.channel.connect()

  ydl_options = {
    'format': 'bestaudio/best',
    'postprocessors': [{
      'key': 'FFmpegExtractAudio',
      'preferredcodec': 'mp3',
      'preferredquality': 192,
    }]
  }

  with yt_dlp.YoutubeDL(ydl_options) as ydl:
    ydl.download([arg])
  
  for file in os.listdir("./"):
    if file.endswith(".mp3"):
      os.rename(file, "song.mp3")
  
  voice.play(discord.FFmpegPCMAudio("song.mp3"))

@bot.command()
async def stop(ctx):
  voice_client = discord.utils.get(bot.voice_clients, guild=ctx.guild)
  
  if voice_client and voice_client.is_connected():
      global voice
      voice.stop()


bot.run(os.environ.get("TOKEN"))