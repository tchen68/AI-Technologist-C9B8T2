(To view the guide in markdown format, either look at it on github or download a markdown preview extension in your IDE.)

# Lab 3 Overview

### RAG Lab

In the last lab, we gave the LLM more context by providing the entire conversation history to the bot. But what happens if we want the bot to generate based on proprietary data that the model does not have access to? This is a good opportunity to leverage Retrieval Augmented Generation (RAG).

Ensure you have properly set up your environment to complete Lab 3. Refer back to `ai-quickstart/README.md` if you need to.

#### First, let's look at the files included in this lab.
        Lab3/
        ├──basic_azure_RAG.py
        ├──basic_vectorization.py
        ├──LAB_3_GUIDE.md (You are here)
        ├──LAB_3_QUESTIONS.md
        ├──data/
        ├──utils/
            ├──utils.py
            ├──vectordb.py

>1. `basic_azure_RAG.py` is the template in which you will create the RAG bot.
>2. `basic_vectorization.py` is where you will ingest the text data, vectorize it, and upload it to your vector database.
>2. `LAB_3_GUIDE.md` This is what you are currently looking at.
>3. `LAB_3_QUESTIONS.md` This is where you should type your responses to the lab questions.
>3. `data/` this is a directory where you can store pure text (.txt) files to ingest into your vector database.
>5. `utils/utils.py` Contains various utilities that we will use in the pipeline, including text processing and LLM functions.
>6. `utils/vectordb.py` Contains functions for interacting with your vector database.

### Code Explanation

In the `basic_vectorization.py` file, we are going to build a simple embedding pipeline that will embed text data from the `data` directory, storing their vectors in a Postgres database.

Before we build the pipeline, we need to load text data into the ```Lab3/data/``` directory to ingest. Create a `test.txt` file in the data directory with a sentence describing your favorite food, starting with "My favorite food is..."

Now that we have data, let's ingest it.

First, we import the following classes:

`from Lab3.utils import utils` (Contains helper functions for interacting with the LLM and text processing.)

`from Lab3.utils import vectordb` (Contains helper functions for interacting with your vector database.)

### 1. Pre-Vectorization Processing

Chunking data before creating embeddings is crucial for handling large texts, improving retrieval accuracy, and ensuring efficiency. By breaking down large texts into smaller chunks, each piece can be processed within the model's token limits, enhancing the model's ability to generate precise and contextually relevant embeddings. This practice also facilitates better indexing and faster retrieval in vector databases, ultimately leading to more accurate and scalable AI applications. Load the data in the file and chunk the text using the provided `utils.basic_character_chunker()` utility function:

```python
    util = utils.Utils()
    text_data = util.read_text_file("test.txt")
    chunks = util.basic_character_chunker(text=text_data, chunk_size=1024)
```
This creates a string of the text found in our ```Lab3/data/test.txt``` file, and then chunks the string based on the set character limit (the default is 1024). This is a very simple version of chunking. More advanced methods of chunking, such as using an LLM to split the text based on relevant blocks of context found and line endings can be used in an effort to improve retrieval and generation accuracy.

Note that the content we are ingesting is very small, so this will result in only 1 chunk being created.

### 2. Vectorization

Take a look at the function ```basic_embedding_generator()``` function in ```utils/utils.py```. This function takes in a chunk of text and calls ```self.azure_openai_client.embeddings.create()``` to generate an embedding of the text. In order to do this, we must pass in the embedding model (e.x. 'text-ada-2') we wish to use and the text to embed. You may notice that before calling the LLM, we call a function named ```normalize_text()```. This function simply removes white space and redundant characters in an effort to improve the retrieval of relevant embeddings. Once a response is received, we access the embedding via response.data[0].embedding.

>Normalizing the text is very important when you intend to generate embeddings from data types that are not pure natural language.

Now that we have a list of text chunks, we want to enumerate these chunks and save the generated embedding alongside its corresponding chunk. Use the following code to build a list of dictionaries containing the text chunks and embeddings:

```python 
    text_and_embeddings = []

    for i, text in enumerate(chunks):
        embedding = util.basic_embedding_generator(input=text)
        text_and_embeddings.append({"text": text, "embedding": embedding})
```

Run ```python -m Lab3.basic_vectorization``` from the root folder (ai-quickstart). Print the text_and_embeddings object and observe it.

**Answer question 1 in ```LAB_3_QUESTIONS.md```.**

### 2. Storing the Vectors

In order to store the embedding for future retrieval, we need a vector database. For this course, we are using the pgvector extension provided by Postgres. Ensure your Postgres credentials are in the .env file. Refer back to `ai-quickstart/README.md` if needed.

In order to use the vector db, we first must initialize it with our vectordb utility class:
```python
    db = vectordb.VectorDB()
    db.init_db()
```

The first call initializes our postgres agent with a connection. `init_db()` then creates a table to store our vectors in the given schema. Embedding dimensions are set to 1536 for this lab. 

Take a look at the ```save_embeddings_in_postgres()``` function in ```utils/vectordb.py```. This function simply takes in the list of dictionaries we created containing the text and embeddings, the name of the vector table, the column name to use for the text chunks, and the column name to use for the embeddings. All of these values default to the standard table and column names we just initialized in ```init_db()```.

Save your recently created embeddings by running the following:
```python
    db.save_embeddings_in_postgres(text_and_embeds=text_and_embeddings, 
                                    table_name="text_chunks", 
                                    text_field='text_content', 
                                    vector_field='embedding')
```

Run ```python -m Lab3.basic_vectorization``` from the root folder (ai-quickstart). 

At this point, your embeddings should be saved in the database. Feel free to check your schema by running a SQL query on the db or connecting to it via any RDMS that accepts Postgres connections.

### 3. Retrieval

Now that we have processed the data and stored it, we can focus on fetching relevant context and generating a response.

Take a look at the ```basic_chat_completion()``` function in ```utils/utils.py.``` We covered this function in previous labs. It simply calls the chat completion model to generate a response with the conversation history as an input.

The following code should go in the ```basic_azure_RAG.py``` file.

Initialize the utils and vectordb classes:
```python
    util=utils.Utils()
    db=vectordb.VectorDB()
```

First, we must construct the initial conversation object with the system role:
```python 
    conversation = [
        {"role": "system", "content": "You are a helpful assistant designed to use the provided additional context and conversation history to assist you in answering the user's prompt."} 
    ]
```

Then, we must retrieve the user's input:
```python
    while True:
        user_input = input("Question: ") 
```

In order to calculate the similarity search against the embeddings we stored in Postgres, we need to generate embeddings for the user's prompt. We then call ```get_embedding_from_postgres()```. This function takes the user prompt embedding and relevant Postgres details to use for the query, runs the Euclidean distance formula on the given vector field, and returns the text associated with the retrieved embedding:

```python
        user_prompt_embedding = util.basic_embedding_generator(user_input)
        context = db.get_embedding_from_postgres(
            user_prompt_embedding,                 
            table_name="text_chunks", 
            text_field='text_content',
            vector_field='embedding')
```

### 4. Generation

Success! Now we have both the user's original input and the retrieved context from our database. We must construct the new message object and append it to the conversation history, and a temporary conversation with the added context:

```python
        user_message = {"role": "user", "content": user_input}
        conversation.append(user_message)

        context_message = {"role": "system", "content": f"Here is some additional context: {context}"}
        conversation_with_context = conversation
        conversation_with_context.append(context_message)
```

>Note: Here we use the 'system' role to append additional context messages to the conversation and ensure it follows the user's newest message. While appending the context directly to the user message can be useful in certain scenarios, it is generally recommended to append the context as a system message to maintain clarity and separation of concerns. This approach ensures that the LLM can clearly distinguish between the user's input and the additional context provided.

We build a temporary conversation object (conversation_with_context) to send to the llm because if we were to append the context provided for every question to the main conversation, we would quickly reach the LLM's context limitations.

Our conversation with context object is now ready to send to the LLM. Call the basic_chat_completion function to retrieve a result, and append the result to the original conversation object:

```python
        llm_response = util.basic_chat_completion(conversation_with_context)
        print(llm_response)

        llm_message = {"role": "assistant", "content": f"{llm_response}"}
        conversation.append(llm_message)
```

Run ```python -m Lab3.basic_azure_RAG``` from the root directory (ai-quickstart). Ask the bot what your favorite food is.

***Answer Question 2-4 in LAB_3_QUESTIONS.md***

Congratulations! You have successfully built a RAG pipeline, starting with ingesting text data into a vector database all the way to context retrieval and generation. We only embedded a small amount of data and implemented a very simple semantic search (Euclidean distance). We highly encourage exploring more advanced methods of RAG implementation, including chunking strategies, prompt chaining, embedding optimizations, and more! Try ingesting larger text documents into the pipeline and asking the bot relevant questions to test its results.

Return to Degreed to continue the course.
