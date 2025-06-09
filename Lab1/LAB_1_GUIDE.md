(To view the guide in markdown format, either look at it on github or download a markdown preview extension in your IDE.)

# Lab 1 Overview

### Basic Azure Completions

In this lab, you will learn how to create simple chat completions using Azure OpenAI.

Ensure you have properly set up your environment to complete Lab 1. Refer back to `ai-quickstart/README.md` if you need to.

#### First, let's look at the files included in this lab.
        Lab1/
        ├──basic_azure_completions.py
        ├──LAB_1_GUIDE.md (You are here)
        ├──LAB_1_QUESTIONS.md

>1. `basic_azure_completions.py` is where you will build the script.
>2. `LAB_1_GUIDE.md` This is what you are currently looking at.
>3. `LAB_1_QUESTIONS.md` This is where you should type your responses to the lab questions.

### Code Explanation

In the `basic_azure_completions.py` file, we are simply providing the LLM a user prompt and system prompt to receive a response. 

First, we import the following libraries:

>1. ```from dotenv import load_dotenv```: Allows us to load our environment variables from the .env file
>2. ```import os```: Allows us to access the environment variables
>3. ```from openai import AzureOpenAI```: Allows us to call our Azure OpenAI endpoint.

We need to load in some of the environment variables to initialize the Azure OpenAI client. Using ```os.environ.get(" <name of environment variable> ")```, load the following variables into the client (lines 11-13):
```python
        azure_endpoint = os.environ.get("OPENAI_API_BASE"),
        api_version = os.environ.get("OPENAI_API_VERSION"),
        api_key = os.environ.get("OPENAI_PROD_API_KEY")
```

**Answer question 1 in ```LAB_1_QUESTIONS.md```**

#### On lines 20 and 21, set the ***user_prompt*** and ***system_prompt*** variables to the following:
```system_prompt="You are a helpful assistant."```

```user_prompt="What is typically included in a healthcare claim?"```

To retrieve a response from the LLM, we must use the ```client``` to call ```chat.completions.create()``` (line 25). To call ```chat.completions.create()```, you must pass in two parameters. The first parameter is the large language model you intend to use through the API, and is simply called ```model```. Pass in the model name from your environment variables file using the same method we used for the client (line 26). 

```python
        model = os.environ.get("OPENAI_API_COMPLETIONS_MODEL"),
```

The second parameter you must pass is the ```messages``` object (line 27). The ```messages``` object is a list of dictionaries. Each dictionary represents a message communicated to the LLM, with a "role" and a "content" field. For this lab, we will simply put two dictionaries in the messages list- one for the system role, and one for the actual user prompt. We will pass in the content using the ```system_role``` and ```user_prompt``` variables that we set earlier:

```python
        messages = [
                {"role": "system", "content": system_role},
                {"role": "user", "content": user_prompt}
        ]
```

Your script is complete! From the root folder (ai-quickstart), run ```python -m Lab1.basic_azure_completions```. Ensure you are in your python virtual environment with the required dependencies installed (see README.md).

**Answer questions 2 & 3 in ```LAB_1_QUESTIONS.md```**

Note the different fields included in the response, including chat id, a list of choice objects, usage statistics and more. The response to the prompt is stored within each choice object in the ```result.choices``` list. The choices list in your responses is likely only 1 in length.

**Answer question 4 in ```LAB_1_QUESTIONS.md```**

Adjust the system role prompt to ```"You are a helpful Meteorology assistant. Only answer questions about Meteorology."``` Rerun the script with a user prompt that has nothing to do with meteorology. Notice the bot's response. 

Now, change the system role prompt to ```"You are a helpful assistant designed to respond in md format."```. Set the user prompt to ```Give me a list of countries and cities in those countries.``` Run the code and look at the response message.

**Answer question 5 in ```LAB_1_QUESTIONS.md```**

Congratulations! You have completed Lab 1 of the AI Technologist Course. Return to the course content in myUniversity to continue.

