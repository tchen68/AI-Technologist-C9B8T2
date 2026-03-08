import os
from openai import OpenAI, APIConnectionError
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

#Initialize the OpenAIClient
try:
    client = OpenAI(
        api_key = 
        base_url = 
    )
    print("OpenAI client initialized succesfully.")
except Exception as e:
    print("Error initializing OpenAI Client:", e) 

#Set system role and prompt
system_role = ''
user_prompt = ''

#Call the AzureOpenAI API
try:
    response = client.chat.completions.create(
        #model = 
        #messages = []
    )

    print(response)
except Exception as e:
    print("Error occured getting response", e)