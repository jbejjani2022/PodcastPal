# retrieve podcast transcripts

import requests
from bs4 import BeautifulSoup
from langchain_community.document_loaders import YoutubeLoader
from settings import transcript_filename


def get_episode_transcript(episode_number):
    # get the transcript of the lex fridman episode from https://karpathy.ai/lexicap/
    # store it in a file, and return the filename
    if int(episode_number) not in range(1,326):
        raise ValueError("The transcript of this episode is not available.")

    number = "0" * (4 - len(episode_number)) + episode_number
    url = f'https://karpathy.ai/lexicap/{number}-large.html'

    # Fetch the content of the URL
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the text content and split it into lines, removing link lines and timestamps
        text = soup.get_text()
        lines = [line[line.rfind('0') + 1 : ]  for line in text.splitlines() if "link |" not in line]
            
        return make_transcript("".join(lines))
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to retrieve the transcript from {url}: {e}")


def get_youtube_video_transcript(url):
    # get the transcript of a youtube video, store it in a file, and return the filename
    loader = YoutubeLoader.from_youtube_url(url)
    transcript = loader.load()
    
    content = transcript[0].page_content
    return make_transcript(content)


def make_transcript(content):
    name = transcript_filename
    with open(name, 'w') as file:
        file.write(content)
    return name
