# chat with an AI bot about the contents of a lex fridman podcast

import requests
from bs4 import BeautifulSoup

episode_number = "420"

def get_episode_transcript(episode_number):
    # get the transcript of the lex fridman episode from https://karpathy.ai/lexicap/
    if episode_number not in range(1,326):
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
            
        return "".join(lines)
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f"Failed to retrieve the transcript from {url}: {e}")


if __name__ == '__main__':
    get_episode_transcript(episode_number)
    with open('transcript.txt', 'w') as file:
        transcript = get_episode_transcript(episode_number)
        # print(transcript)
        file.write(transcript)