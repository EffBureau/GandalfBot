"""This module downloads the quotes necessary to download Gandalf's quotes"""
import glob
import json
import os

import requests
from bs4 import BeautifulSoup


class Quotes():
    """This class handles the downloading of quotes for gandalf."""
    dirname = os.path.dirname(__file__)

    @classmethod
    def download_quotes(cls):
        """
            Downloads all the quotes from http://www.theargonath.cc/characters/gandalf/sounds/sounds.html 
            and puts them in the quotes folder. 
        """

        # Find all .wav files
        files = glob.glob(os.path.join(cls.dirname, "../../quotes/*.wav"))

        # Check if files are empty
        if not any(files):

            # Page content
            url = "http://www.theargonath.cc/characters/gandalf/sounds/sounds.html"
            page = requests.get(url, allow_redirects=True, timeout=5000)

            filenames = []
            soup = BeautifulSoup(page.content, "html.parser")

            # For each file to download
            for a_href in soup.find_all("a", href=True):
                if "html" not in a_href["href"]:
                    request = requests.get(
                        a_href["href"], allow_redirects=True, timeout=5000)

                # Split the link to get file name
                split_link = a_href["href"].split('/')
                quote = split_link[len(split_link) - 1]

                # Create file
                open(os.path.join(cls.dirname, "../../quotes", quote),'wb').write(request.content)
                filenames.append(quote)

            # Dump all file names in a .json file
            with open(os.path.join(self.dirname, '../../quotes.json'), 'w') as outfile:
                json.dump(filenames, outfile)