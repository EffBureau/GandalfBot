"""This module downloads the quotes necessary to download Gandalf's quotes"""
import glob
import json
import os

import requests
from bs4 import BeautifulSoup


class quotes():
    """This class handles the downloading of quotes for gandalf."""
    dirname = os.path.dirname(__file__)

    @classmethod
    def download_quotes(cls):
        """
            Downloads all the quotes from http://www.theargonath.cc/characters/gandalf/sounds/sounds.html 
            and puts them in the quotes folder. 
        """
        files = glob.glob(os.path.join(cls.dirname, "../../quotes/*.wav"))

        if not any(files):
            url = "http://www.theargonath.cc/characters/gandalf/sounds/sounds.html"
            page = requests.get(url, allow_redirects=True, timeout=5000)

            filenames = []
            soup = BeautifulSoup(page.content, "html.parser")

            for a_href in soup.find_all("a", href=True):
                if "html" not in a_href["href"]:
                    request = requests.get(a_href["href"], allow_redirects=True, timeout=5000)

                split_link = a_href["href"].split('/')
                quote = split_link[len(split_link) - 1]

                open(os.path.join(cls.dirname, "../../quotes", quote),'wb').write(request.content)
                filenames.append(quote)

            with open(os.path.join(cls.dirname, '../quotes.json'), 'w', encoding='utf-8') as outfile:
                json.dump(filenames, outfile)
