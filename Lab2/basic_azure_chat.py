import os
from openai import AzureOpenAI
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

#initialize the AzureOpenAI Client
try:
  client = AzureOpenAI(
    azure_endpoint = ,
    api_version = ,
    api_key = 
  )
  print("OpenAI client initialized succesfully.")
except Exception as e:
  print("Error initializing OpenAI Client:", e)

#This function is the same as the script we built in lab 1, however now we pass in the conversation history as a parameter.
def basic_chat_completion(conversation:list=None):
    try:
        response = client.chat.completions.create(
            model = os.environ.get("OPENAI_API_COMPLETIONS_MODEL"),
            messages=conversation,
                )
        if response.statusCode == 400:
            raise Exception("Bad request. Please check your input.")
        return response
    except Exception as e:
      print("Error during chat completion:", e)
      return None
    
#Set the system role by appending it as the first message of the conversation history.
conversation=[]

#Build a loop that keeps the chat open until user exits the chat and appends user\bot messages to the conversation history.