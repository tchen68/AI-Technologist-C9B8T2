import os
from openai import OpenAI
from dotenv import load_dotenv

# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================
load_dotenv()

# =====================================================
# LAB TEST SETTINGS
#
# Normal Lab Run:
#     USE_GPT4O = False
#     USE_MAX_TOKENS = False
#
# Max Token Exercise:
#     USE_MAX_TOKENS = True
#
# Temperature Exercise:
#     USE_GPT4O = True
#     TEMPERATURE = 0
#     OR
#     TEMPERATURE = 1
# =====================================================

USE_GPT4O = False
USE_MAX_TOKENS = False

MAX_TOKENS = 50
TEMPERATURE = 0

# =====================================================
# INITIALIZE OPENAI CLIENT
# =====================================================
try:

    client = OpenAI(
        api_key=os.environ.get("AI_GW_API_KEY"),
        base_url=os.environ.get("AI_GW_BASE_URL")
    )

    print("OpenAI client initialized successfully.")

except Exception as e:

    print(f"Error initializing OpenAI client: {e}")
    exit()

# =====================================================
# CHAT COMPLETION FUNCTION
# =====================================================
def basic_chat_completion(conversation: list = None):

    try:

        # ---------------------------------------------
        # TEMPERATURE EXERCISE
        # GPT-4o ONLY
        # ---------------------------------------------
        if USE_GPT4O:

            response = client.chat.completions.create(
                model="gpt-4o",
                messages=conversation,
                temperature=TEMPERATURE
            )

            return response

        # ---------------------------------------------
        # MAX TOKEN EXERCISE
        # ---------------------------------------------
        elif USE_MAX_TOKENS:

            response = client.chat.completions.create(
                model=os.environ.get("COMPLETIONS_MODEL"),
                messages=conversation,
                max_tokens=MAX_TOKENS
            )

            return response

        # ---------------------------------------------
        # NORMAL LAB EXECUTION
        # ---------------------------------------------
        else:

            response = client.chat.completions.create(
                model=os.environ.get("COMPLETIONS_MODEL"),
                messages=conversation
            )

            return response

    except Exception as e:

        print(f"Error during chat completion: {e}")
        return None


# =====================================================
# CONVERSATION HISTORY
# =====================================================
conversation = [
    {
        "role": "system",
        "content": "You are a helpful assistant."
    }
]

# =====================================================
# START CHAT
# =====================================================
print("\n=================================================")
print(" Lab 2 - LLM Conversation Chat")
print("=================================================")
print("Type 'exit' or 'quit' to stop.\n")

# =====================================================
# MAIN CHAT LOOP
# =====================================================
while True:

    user_input = input("Question: ").strip()

    # Exit Chat
    if user_input.lower() in ["exit", "quit"]:
        print("\nEnding conversation...")
        break

    # Ignore Empty Inputs
    if not user_input:
        print("Please enter a question.\n")
        continue

    # Add User Message
    conversation.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Send Conversation History to LLM
    response = basic_chat_completion(conversation)

    # Process Response
    if response:

        bot_message = response.choices[0].message.content

        # Store Assistant Response
        conversation.append(
            {
                "role": "assistant",
                "content": bot_message
            }
        )

        print("\nAssistant:")
        print(bot_message)
        print()

    else:

        print("No response from assistant.\n")