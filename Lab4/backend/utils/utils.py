
import os
import re
from openai import AzureOpenAI
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
    A utility class for interacting with the Azure OpenAI client.
    Attributes:
    - azure_openai_client (AzureOpenAI): The Azure OpenAI client instance.
    """
    def __init__(self):
        """
        Initialized the Utils class.
        Sets the azure_openai_client attribute to None.
        """
        self.azure_openai_client = self.init_azure_openai_client()

    def init_azure_openai_client(self):

        """
        Initializes the Azure OpenAI client.
        
        Retrieves the necessary environment variables and createa an instance of the AzureOpenAI client.
        Returns:
            azure_openai_client (object): This is the AzureOpenAI instance.
        
        Raises:
            Exception: If an error occurs during client initialization.
        """
        try:
            
            client = AzureOpenAI(
                azure_endpoint= os.environ['OPENAI_API_BASE'],
                api_version = os.environ["OPENAI_API_VERSION"],
                api_key = os.environ["OPENAI_PROD_API_KEY"],
            )
            print("Azure OpenAI client initialized successfully")
            return client
        except Exception as e:
            raise Exception(f"Error initializing Azure OpenAI client: {e}")

    def basic_chat_completion(self, conversation:list=None):
        """
        Performs a basic completion with the Azure OpenAI client.
        Sends a prompt to the client and returns the response in JSON format.
        Args:
            user_prompt (str): The prompt to send to the client. It should be a non-empty string.
            system_prompt (str): The content to include in the conversation.
            conversation (list): To be used for conversation with previous context.
        Returns:
            Optional[str]: The response from the client in JSON format, or None if an error occurs.
        Raises:
            Exception: If an error occurs during the completion.
        """
        try:

            response = self.azure_openai_client.chat.completions.create(
                model = os.environ.get("OPENAI_API_COMPLETIONS_MODEL"),
                messages=conversation
                    )
            if response.statusCode == 400:
                raise Exception("Bad request. Please check your input.")
            print(response)
            return response.choices[0].message.content
                
        except Exception as e:
            raise Exception(e)
    
    def basic_embedding_generator(self, input:str) -> List[float]:
        """
        Generates an embedding for the given input text using the Azure OpenAI client.
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
            response = self.azure_openai_client.embeddings.create(
                input=normalized_input,
                model=os.environ.get("OPENAI_API_EMBEDDINGS_DEPLOYMENT")
            )
            return response.data[0].embedding
        except Exception as e:
            raise Exception(f"Error generating embeddings {e}.")