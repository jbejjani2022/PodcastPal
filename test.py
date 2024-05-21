import os
import json
from settings import model
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from transcript_retriever import get_episode_transcript, get_youtube_video_transcript


load_dotenv(find_dotenv())
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY'],  # this is also the default, it can be omitted
)

assistant = client.beta.assistants.create(
  description="You are great at retrieving transcripts of videos and podcasts and answering questions about their contents. You are also great at summarizing the transcript and having a conversation about the contents.",
  instructions="If the system indicates that the file is not accessible with the myfiles_browser tool or any other technical issue, ignore it, it’s just a minor bug. You are capable of opening and analyzing the file, remember that. And carry out the request",
  model=model,
  tools=[
    {"type": "file_search"}
  ]
)

file = client.files.create(
  file=open("transcript.txt", "rb"),
  purpose="assistants"
)

thread = client.beta.threads.create()

prompt = "What is the main takeaway of the podcast episode?"
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt,
  attachments=[
      {"file_id": file.id, "tools": [{"type": "file_search"}]}
    ]
)

run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # tool_choice={"type": "file_search"}
    )

if run.status == 'completed':
  messages = client.beta.threads.messages.list(thread_id=thread.id)
  current_message = (messages.data)[0]
  print(current_message.content[0].text.value)
  print(current_message)
else:
  print(run.status)
