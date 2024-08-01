# PodcastPal

PodcastPal is a way to summarize a long video or episode to save time, refresh your memory on the topic of a video or episode,
or further your learning and understanding of the video or episode's contents. Also see my related [SummarizerAssistant](https://github.com/jbejjani2022/SummarizerAssistant.git) repo. 

I used OpenAI's Assistant API to make calls to tools that extract transcripts of YouTube videos and Lex Fridman 
podcast episodes; the transcript then functions as a knowledge base for subsequent prompts. This allows the user to 
ask about the contents of the video or episode and build a thread with persistent chat history.

Setup:  
Create a file named `.env` with contents `OPENAI_API_KEY = "Your OpenAI API key"`.

Usage:  
In `podcastpal.py`, modify the initial prompt with the YouTube URL or Lex Fridman podcast episode number you're interested in.
Build your own chat by modifying and/or adding subsequent prompts and messages that inquire about the episode,
and creating `run`s to generate the assistant's response for each new message.
