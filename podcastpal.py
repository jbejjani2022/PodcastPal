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

def run_thread():
    print(assistant)
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    if run.status == 'completed':
      messages = client.beta.threads.messages.list(thread_id=thread.id)
      current_message = (messages.data)[0]
      print(current_message.content[0].text.value)
      # print(current_message)
    else:
      print(run.status)
      
    return run


prompt = "Let's chat about Lex Fridman podcast episode #315."
# prompt = "Let's chat about https://www.youtube.com/watch?v=N9XKz9RBxGU"

thread = client.beta.threads.create()
message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt
)

run = run_thread(assistant)
 
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
    
    # Create a vector store
    vector_store = client.beta.vector_stores.create(name="transcripts")
      
    # Ready transcript file(s) for upload to OpenAI
    file_paths = [tool_output["output"] for tool_output in tool_outputs]
    file_streams = [open(path, "rb") for path in file_paths]
      
    # Use the upload and poll SDK helper to upload the files, add them to the vector store,
    # and poll the status of the file batch for completion.
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id=vector_store.id, files=file_streams
    )
      
    # You can print the status and the file counts of the batch to see the result of this operation.
    print(f'File batch status: {file_batch.status}')
    print(f'File batch counts: {file_batch.file_counts}')
      
    # Update the assistant’s tool_resources with the new vector_store id
    # to make the files accessible to the assistant
    assistant = client.beta.assistants.update(
      assistant_id=assistant.id,
      tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )
    
  except Exception as e:
    print("Failed to submit tool outputs:", e)
else:
  print("No tool outputs to submit.")

if run.status == 'completed':
  messages = client.beta.threads.messages.list(thread_id=thread.id)
  current_message = (messages.data)[0]
  print(current_message.content[0].text.value)
else:
  print(run.status)

# files = [client.files.create(file=f, purpose="assistants") for f in file_streams]
# attachments= [{ "file_id": f.id, "tools": [{"type": "file_search"}] } for f in files]
# file = client.files.create(file = open("transcript.txt", "rb"), purpose="assistants")
# atts = [{ "file_id": file.id, "tools": [{"type": "file_search"}] }]

prompt2 = "Summarize the attached file."

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt2
)

run_thread(assistant)
  
prompt3 = "Who are the speakers in the video according to attached file?"

message = client.beta.threads.messages.create(
  thread_id=thread.id,
  role="user",
  content=prompt3
)

run_thread(assistant)
