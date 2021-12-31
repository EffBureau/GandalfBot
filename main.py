import discord
from discord import FFmpegPCMAudio
import random
import glob, os
from bs4 import BeautifulSoup
import requests
from requests.structures import CaseInsensitiveDict
from discord.ext.commands import Bot
import json
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
client = Bot("!")

headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Authorization"] = "Bearer JQ6KMVxKnmWdTxYZYax3"

quotes = []

with open('quotes.json') as json_quotes:
  quotes.extend(json.load(json_quotes))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):    
    if message.author == client.user:
        return

    if "gandalf" in message.content:
      if message.author.voice.channel not in client.voice_clients :
        voice = await message.author.voice.channel.connect()
        source = FFmpegPCMAudio(os.path.join("quotes", quotes[random.randint(0, len(quotes) - 1)]), executable=os.environ.get("FFMPEG_PATH"))
        player = voice.play(source)
      else:
        voice = client.voice_clients[0]
        source = FFmpegPCMAudio(quotes[random.randint(0, len(quotes) - 1)])
        player = voice.play(source)

client.run(os.environ.get("TOKEN"))