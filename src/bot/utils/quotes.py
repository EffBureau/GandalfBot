from bs4 import BeautifulSoup
import glob, os
import requests
import os
import json

class Quotes():

    dirname = os.path.dirname(__file__)

    @classmethod
    def download_quotes(self):
        # Find all .wav files
        files = glob.glob(os.path.join(self.dirname, "../../quotes/*.wav"))

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
                    r = requests.get(a_href["href"], allow_redirects=True)

                # Split the link to get file name
                split_link = a_href["href"].split('/')
                quote = split_link[len(split_link) - 1]

                # Create file
                open(os.path.join(self.dirname, "../../quotes", quote), 'wb').write(r.content)
                filenames.append(quote)

            # Dump all file names in a .json file
            with open(os.path.join(self.dirname, '../../quotes.json'), 'w') as outfile:
                json.dump(filenames, outfile)