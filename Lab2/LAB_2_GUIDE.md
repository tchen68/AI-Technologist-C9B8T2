(To view the guide in markdown format, either look at it on github or download a markdown preview extension in your IDE.)

# Lab 2 Overview

### LLM Conversational Chat 

In the last lab, we saw how to generate a response by the LLM for a given user and system prompt, and what happens to the LLM's behavior when we adjust those prompts. In this lab, we will take it one step further and create a bot that maintains conversation history with the user to provide more relevant responses.

Ensure you have properly set up your environment to complete Lab 2. Refer back to `AITechnologistLabs/README.md` if you need to.

#### First, let's look at the files included in this lab.
        Lab2/
        ├──basic_azure_chat.py
        ├──LAB_2_GUIDE.md (You are here)
        ├──LAB_2_QUESTIONS.md

>1. `basic_azure_chat.py` is the template in which you will write the script.
>2. `LAB_2_GUIDE.md` This is what you are currently looking at.
>3. `LAB_2_QUESTIONS.md` This is where you should type your responses to the lab questions.

### Code Explanation

In the `basic_azure_chat.py` file, we are simply providing the conversation history to the LLM instead of just the system role and one user prompt in lab 1. The conversation history is just the messages object discussed in the previous lab, however we append the user prompt and LLM response to the messages list as they are received. As a result, the LLM is able to use the conversation history as context to the new prompt and even call back to previous prompts or responses.

First, we import the following libraries:

>1. ```from dotenv import load_dotenv```: Allows us to load our environment variables from the .env file
>2. ```import os```: Allows us to access the environment variables
>3. ```from openai import AzureOpenAI```: Allows us to call our Azure OpenAI endpoint.

We need to load in some of the environment variables to initialize the Azure OpenAI client. Load in the API base, version, and key as we did in lab 1 (lines 11-13).

The ```basic_chat_completion()``` function (20-31) is the same as the script you built in lab 1, however we have built it into a function with ```conversation``` as an input. 

Before we begin conversing with the LLM, it is important that we still set the system role before any user prompting. Set the first object in the ```conversation``` list to the system role, with the content "You are a helpful assistant." (line 34). 

Now, we must build a loop that takes in a user's prompt, appends it to the ```conversation``` object, calls ```basic_chat_completion``` to receive a response, then appends that to the ```conversation```, outputs it to the user, and re-prompts them. Build this loop following the instructions below.

1. First, we must retrieve the user's input and append it to the conversation_history list:
   
```python
    while True:
        user_input = input("Question: ") 
        conversation.append({"role": "user", "content": user_input})
```

2.  Once we have received a prompt, we must call the ```basic_chat_completions``` function, passing in ```conversation``` as a parameter. Save this to the "response" variable.

```python
        response = basic_chat_completions(conversation)
```

3. If a response is returned, we must append it to the conversation history using the "assistant" role and output it to the user:
```python
        if response:
            bot_message = response.choices[0].message.content
            conversation.append({"role": "assistant", "content": bot_message})
            print("\n" + bot_message + "\n")
        else:
            print("No response from the assistant.")
``` 

Congratulations! Your script is complete. From the root folder (AITechnologistLabs), run ```python -m Lab2.basic_azure_chat```. Ensure you are in your python virtual environment with the required dependencies installed (see README.md).

**Answer questions 1-2 in ```LAB_2_QUESTIONS.md```**

Ask the script to return a list of countries and their cities. 

At this point, the script should have immediately re-prompted you. Ask the script to turn its last response into a md string.

**Answer question 3 in ```LAB_2_QUESTIONS.md```**

Ask the bot to write a 5000 word essay about the sky. Pay close attention to what the output says. 

Now, ask the bot to generate a 100 word essay about the sky.

In ```client.chat.completions.create()```, add the 'max_tokens' parameter and set it to 50 

ex.
```python    
    response = client.chat.completions.create(
        model = os.environ.get("OPENAI_API_COMPLETIONS_MODEL"),
        messages=conversation,
        max_tokens=50
)
```

Again, ask the bot to generate a 100 word essay about the sky.

**Answer question 4 in ```LAB_2_QUESTIONS.md```**

Remove the max token parameter, and instead, replace it with the ```temperature``` parameter. Temperature is a scalar (0 to 1) that allows us to control the 'randomness' of the LLM. A lower temperature results in more predictable and consistent responses, while a higher temperature value results in more diverse and creative responses.

ex.
```python    
    response = client.chat.completions.create(
        model = os.environ.get("OPENAI_API_COMPLETIONS_MODEL"),
        messages=conversation,
        temperature=0
)
```

First, set the temperature to 0 and ask the LLM to list 3 creative uses for a paperclip.

Then set the temperature to 1 and ask the LLM the same question.

**Answer question 5 in ```LAB_2_QUESTIONS.md```**

Congratulations! You have completed Lab 2 of the AI Technologist Course. Return to the course content in myUniversity to continue.

