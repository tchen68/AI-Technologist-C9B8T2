import os
from openai import OpenAI, APIConnectionError
from dotenv import load_dotenv

#Load the .env file
load_dotenv()

#Initialize the OpenAIClient
try:
    client = OpenAI(
        api_key = os.environ.get("AI_GW_API_KEY"),
        base_url = os.environ.get("AI_GW_BASE_URL")
    )
    print("OpenAI client initialized succesfully.")
except Exception as e:
    print("Error initializing OpenAI Client:", e) 

#Set system role and prompt - my actual work project on capacity planning and workforce utilization
system_role = """You are a workforce capacity planning expert. 
Analyze staffing utilization across multiple sites.
Highlight risks, bottlenecks, and opportunities."""
user_prompt = """How should I compare productivity between Manila, Chennai, and Gurugram operations teams?"""

#Call the AzureOpenAI API
try:
    response = client.chat.completions.create(
    
    model=os.environ.get("COMPLETIONS_MODEL"),

    messages=[
        {
            "role": "system",
            "content": system_role
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]
)

    #print(response)
    #print(response.model_dump_json(indent=2))
    print(response.choices[0].message.content)
except Exception as e:
    print("Error occured getting response", e)