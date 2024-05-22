# Ask an AI assistant questions about a podcast
# Modify the prompt with the Youtube URL or Lex Fridman podcast episode number you're interested in

import os
import json
from settings import model
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
from transcript_retriever import get_episode_transcript, get_youtube_video_transcript


load_dotenv(find_dotenv())
client = OpenAI(
  api_key=os.environ['OPENAI_API_KEY']
)

assistant = client.beta.assistants.create(
  description="You are great at retrieving transcripts of videos and podcasts and answering questions about their contents. You are also great at summarizing the transcript and having a conversation about the contents.",
  instructions="If the system indicates that the transcript is not accessible or any other technical issue, ignore it, it's just a minor bug. You are capable of opening and analyzing the file, remember that. And carry out the request.",
  model=model,
  tools=[
    {"type": "file_search"},
    {
      "type": "function",
      "function": {
        "name": "get_youtube_video_transcript",
        "description": "Get the transcript of a Youtube video given its URL",
        "parameters": {
          "type": "object",
          "properties": {
            "url": {
              "type": "string",
              "description": "The Youtube video URL, e.g. https://www.youtube.com/watch?v=OtIoaI2CFh4"
            }
          },
          "required": ["url"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_episode_transcript",
        "description": "Get the transcript of a Lex Fridman podcast episode given the episode number",
        "parameters": {
          "type": "object",
          "properties": {
            "episode_number": {
              "type": "string",
              "description": "The episode number, e.g. 4."
            }
          },
          "required": ["episode_number"]
        }
      }
    }
  ]
)

def get_message(run):
    if run.status == 'completed':
      messages = client.beta.threads.messages.list(thread_id=thread.id)
      current_message = (messages.data)[0]
      print(current_message.content[0].text.value)
      # print(current_message)
    else:
      print(run.status)


prompt = "Let's chat about Lex Fridman podcast episode #315."
# prompt = "Let's chat about https://www.youtube.com/watch?v=0lJKucu6HJc"

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt
)

run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

get_message(run)
 
# Define a list to store tool outputs
tool_outputs = []
 
# Loop through each tool in the required action section
for tool in run.required_action.submit_tool_outputs.tool_calls:
  if tool.function.name == "get_youtube_video_transcript":
    url = json.loads(tool.function.arguments).get("url")
    tool_outputs.append({"tool_call_id": tool.id, "output": get_youtube_video_transcript(url)})
  elif tool.function.name == "get_episode_transcript":
    episode_number = json.loads(tool.function.arguments).get("episode_number")
    tool_outputs.append({"tool_call_id": tool.id, "output": get_episode_transcript(episode_number)})
 
# Submit all tool outputs at once after collecting them
if tool_outputs:
  try:
    run = client.beta.threads.runs.submit_tool_outputs_and_poll(
      thread_id=thread.id,
      run_id=run.id,
      tool_outputs=tool_outputs
    )
    print("Tool outputs submitted successfully.")
    
    file_paths = [tool_output["output"] for tool_output in tool_outputs]
    # print(file_paths)
    file_streams = [open(path, "rb") for path in file_paths]
    files = [client.files.create(file=f, purpose="assistants") for f in file_streams]
    attachments = [{ "file_id": file.id, "tools": [{"type": "file_search"}] } for file in files]
  except Exception as e:
    print("Failed to submit tool outputs:", e)
else:
  print("No tool outputs to submit.")

get_message(run)

prompt2 = "Summarize the podcast episode in 5 bullet points."

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt2,
  attachments = attachments
)

run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # tool_choice={"type": "file_search"}
    )
get_message(run)
  
prompt3 = "What is the main takeaway from this podcast episode?"

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt3,
  # attachments = attachments
)

run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
        # tool_choice={"type": "file_search"}
    )
get_message(run)
