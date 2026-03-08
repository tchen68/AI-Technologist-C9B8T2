import os
from openai import OpenAI
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

#initialize the OpenAI Client
try:
  client = OpenAI(
    api_key = os.environ.get("AI_GW_API_KEY"),
    base_url = os.environ.get("AI_GW_BASE_URL"),
  )
  print("OpenAI client initialized succesfully.")
except Exception as e:
  print("Error initializing OpenAI Client:", e)

#This function is the same as the script we built in lab 1, however now we pass in the conversation history as a parameter.
def basic_chat_completion(conversation:list=None):
    try:
        response = client.chat.completions.create(
            model = os.environ.get("COMPLETIONS_MODEL"),
            messages=conversation,
        )
        return response
    except Exception as e:
      print("Error during chat completion:", e)
      return None
    
#Set the system role by appending it as the first message of the conversation history.
conversation=[]

#Build a loop that keeps the chat open until user exits the chat and appends user\bot messages to the conversation history.