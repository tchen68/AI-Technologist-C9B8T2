
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv("chatbot.env")

def normalize_text(input_text):
    input_text = re.sub(r'\s+',  ' ', input_text).strip()
    input_text = re.sub(r". ,","",input_text)
    input_text = input_text.replace("..",".")
    input_text = input_text.replace(". .",".")
    input_text = input_text.replace("\n", "")
    input_text = input_text.strip()
    return input_text

class Utils:
    """
    A utility class for interacting with the OpenAI client.
    Attributes:
    - openai_client (OpenAI): The OpenAI client instance.
    """
    def __init__(self):
        """
        Initialized the Utils class.
        Sets the openai_client attribute.
        """
        self.openai_client = self.init_openai_client()

    def init_openai_client(self):

        """
        Initializes the OpenAI client.
        
        Retrieves the necessary environment variables and creates an instance of the OpenAI client.
        Returns:
            openai_client (object): This is the OpenAI instance.
        
        Raises:
            Exception: If an error occurs during client initialization.
        """
        try:
            
            client = OpenAI(
                api_key = os.environ.get("AI_GW_API_KEY"),
                base_url = os.environ.get("AI_GW_BASE_URL"),
            )
            print("OpenAI client initialized successfully")
            return client
        except Exception as e:
            raise Exception(f"Error initializing OpenAI client: {e}")

    def basic_chat_completion(self, conversation:list=None):
        """
        Performs a basic completion with the OpenAI client.
        Sends a prompt to the client and returns the response.
        Args:
            user_prompt (str): The prompt to send to the client. It should be a non-empty string.
            system_prompt (str): The content to include in the conversation.
            conversation (list): To be used for conversation with previous context.
        Returns:
            Optional[str]: The response from the client, or None if an error occurs.
        Raises:
            Exception: If an error occurs during the completion.
        """
        try:
            response = self.openai_client.chat.completions.create(
                model = os.environ.get("COMPLETIONS_MODEL"),
                messages=conversation
            )
            print(response)
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(e)
    
    def basic_embedding_generator(self, input:str) -> List[float]:
        """
        Generates an embedding for the given input text using the OpenAI client.
        Args:
            input (str): The input text to generate an embedding for. Defaults to None.
        Returns:
            the generated embedding.
        Example:
            >>> utils = Utils()
            >>> prompt = "This is an example sentence."
            >>> embeddings = utils.basic_embedding_generation(prompt)
            >>> print(embeddings['data'][0]['embedding'])
        """

        #removes redundant whitespace and cleaning up the punctuation to prepare the data for tokenization
        normalized_input = normalize_text(input)

        try:
            response = self.openai_client.embeddings.create(
                input=normalized_input,
                model=os.environ.get("EMBEDDINGS_MODEL"),
                dimensions=1536
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embeddings {e}.")