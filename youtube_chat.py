from langchain_community.document_loaders import YoutubeLoader

youtube_url = "https://www.youtube.com/watch?v=OtIoaI2CFh4"


def get_youtube_video_transcript(url):
    loader = YoutubeLoader.from_youtube_url(url)
    transcript = loader.load()
    
    return transcript[0].page_content


if __name__ == '__main__':
    with open('transcript.txt', 'w') as file:
        transcript = get_youtube_video_transcript(youtube_url)
        print(transcript)
        file.write(transcript)