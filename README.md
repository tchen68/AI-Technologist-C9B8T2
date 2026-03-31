# AI Quickstart

#### This repo contains labs for the AI Technologist Course.
---

## Prerequisites
You should have a python development environment set up (i.e. an installation of python and an IDE of your choice). The labs have been tested through python version <=3.13 to ensure package compatibility.

To use any of the labs in this repository, you will first need to get an Azure OpenAI endpoint for Cigna's AI Gateway. Details regarding accessing your API are in the cohort kickoff communication.

Labs 3 & 4 require a vector database. This has also been provisioned for you upon cohort kickoff. Find instructions on how to get your credentials in the cohort kickoff communication.

# Getting Started

## Environment Variables

### LiteLLM Gateway endpoint 
The AI COE provides access to LLM models via the LiteLLM Gateway. For exploration lab support and documentation, click [here](https://iris.thecignagroup.com/home/ls/content/6182343247640281/from-hours-to-seconds-exploration-lab-user-access). For this course, we recommend using gpt-5:

                AI_GW_BASE_URL = "https://litellm.ai-coe-test.aws.evernorthcloud.com/v1"
                AI_GW_API_KEY = "<Retrieved from AI COE>"
                COMPLETIONS_MODEL = "gpt-5"
                EMBEDDINGS_MODEL = "text-embedding-3-large"

### Postgres endpoint
This course uses the pgvector extension of postgres hosted on Unity to serve as a vector database in Lab 3 and 4. At the start of the course, you should have recieved an automated webex message from HIHBot providing the necessary credentials for your personal database schema. Please put those in the .env file accordingly:

                PG_DB_USERNAME = "<provided by HIHBot>"
                PG_DB_PASSWORD = "<provided by HIHBot>"
                PG_DB_HOST = "<provided by HIHBot>"
                PG_DB_NAME = "<provided by HIHBot>"
                PG_DB_PORT = "<Provided by HIHBot>"
                PG_DB_SCHEMA = "<provided by HIHBot>"

If you did not recieve your credentials or believe there is an error, please reach out to the course administrators.

In *.env.sample*, paste in your environment variables from AI Studio. 

**Rename the ```sample.env``` file to ```.env```**

NOTE: Postgres credentials are only needed for labs involving RAG (lab 3 & 4).

### Virtual Environment Setup

In the repository root directory (`AITechnologistLabs`), create a Python virtual environment:

```sh
python -m venv .venv
```

To activate the virtual environment, run the following:

For Mac:
```sh
source .venv/bin/activate
```

For Windows:
```sh
.venv\Scripts\activate
```

Once you have activated your virtual environment, you must install the required dependencies. To do so, run the following:

```sh
pip install -r requirements.txt
```

## Labs

There are 4 labs included in this repository.

1. **Basic Completions**
   
    Learn how to call the LLM via the LiteLLM Gateway for chat completions. Learn how to interpret the API response, and how to adjust system and user prompts to receive different response formats and constraints. 

2. **Basic LLM Chat**
   
    Now that we know how to fetch chat completions and interpret the response, we increase the complexity of the bot by providing the conversation history as context when prompting for a completion. We also modularize some of the utility code to follow development best practices.

3. **Basic RAG Pipeline**

    What if we need the LLM to answer questions on not publicly available data, and fine-tuning/training a custom model is not an option? Enter Retrieval Augmented Generation (RAG). In this module, you will learn how to implement a simple RAG pipeline for your AI applications. 

4. **Full-Stack Chat Bot**

    In this module, we take what we learned about building applications with LLMs and apply it to build a full-stack chatbot with React and Flask API.

## HOW TO SEND LABS FOR REVIEW

Details on submitting your labs for certification grading will be shared by the administrators at a later point in the cohort. If you finish before this is communicated, please reach out to AITechnologistCertification@evernorth.com

## ENSURE YOU DO NOT ACCIDENTALLY UPLOAD ANY ENVIRONMENT VARIABLES OR SENSITIVE INFORMATION.

---

## Appendix: Historical Issues

### SSL Certificate Issues (Legacy Azure OpenAI Gateway)

> **Note:** This section is only relevant if you are using the legacy Azure OpenAI Gateway endpoint (not the LiteLLM Gateway). The LiteLLM Gateway should not require these steps.

If you run into SSL issues when calling the LLM (ex. [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate):

1. Navigate to https://github.sys.cigna.com/cigna/certfix 
2. Either follow their guide to install the cigna.pem file into your virtual environment or follow the instructions below:
    1. In the certfix repository on github, navigate to the cigna.pem file. Copy ALL of its contents (Ctrl+C)
    2. Go to your virtual environment directory. Navigate to ~/site-packages/certifi/cacert.pem on Windows or ~/lib/python3.X/site-packages/certifi/cacert.pem on Mac
    3. Append the contents from the cigna.pem file into the cacert.pem file. DO NOT DELETE OR EDIT THE EXISTING CERTS IN cacert.pem.
    4. Save All and rerun the lab. Reach out to the course administrators if you still run into issues.

