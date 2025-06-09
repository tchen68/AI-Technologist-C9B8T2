# Chatbot Guide

In this lab, we will take the retrival method we built for our vector database to build a full-stack RAG Chatbot!

## Prerequisites

1. Configure ai-quickstart\Lab4\backend\chatbot.env with the same credentials you used in the previous labs.
2. If you haven't already, install requirements from ai-quickstart\requirements.txt into your virtual environment (See README.md). Ensure you activate the environment. 
3. Download and install Node.js via the Cigna FOSS self-service portal or via the web: https://docs.npmjs.com/downloading-and-installing-node-js-and-npm

## Getting Started

#### Now that you have training in beginner and intermediate Generative AI development, let's apply that knowledge to a full-stack application. In this lab, you will learn how to create a full-stack application by implementing your RAG bot into a React frontend and simple backend with Flask API service.

While there are many frontend libraries you can use to build your chatbot, we will be using React in this lab. React is a widely-adopted open-source JavaScript library for web and native user interfaces. React lets you build UIs out of individual components, enabling reusability for common components and efficiently managing application state and rendering. You can learn more about React here: https://react.dev/learn

There are also many different web frameworks we can use for our frontend to interact with our backend, but in this lab we will be using Flask. Flask is a popular web framework used to design APIs, microservices, and more: https://flask.palletsprojects.com/en/3.0.x/

## Backend

#### First, let's look at the backend folder structure.
        Lab4/
        ├── backend/
        |   ├──app.py
        |   ├──chatbot.env 
        |   └──utils/
        |      ├── vectordb.py
        |      └── utils.py    

#### 1. `app.py` is our main script for the backend. It contains instructions for our Restful API to send and receive data with the frontend.
#### 2. `chatbot.env` is a standard environment variable file. This is where you should keep your keys and credentials for the scripts to reference.
#### 3. `utils\utils.py` contains utility functions for connecting and calling the LLM (app.py imports and uses these in its instructions). This is the same utility we used in Lab 3.
#### 4. `utils\vectordb.py` contains utility functions for interfacing with the vector db. This is the same db util we used in Lab 3.

## Frontend

#### Let us take a look at the frontend folder structure.
        Lab4/
        ├── chatbot-ui/
        |   ├──node_modules/
        |   ├──public/
        |   ├──src/
        |   |  ├──components/
        |   |  ├──scenes/
        |   |  |  └──chatbot.jsx
        |   |  ├──App.css
        |   |  ├──App.js
        |   |  ├──index.css
        |   |  ├──index.js
        |   ├──package.md
        |   ├──package-lock.md

#### 1. `node_modules/` folder stores all dependencies (packages and libraries) your application requires to run. This is automatically managed by npm.
#### 2. `public/` typically stores common image resources and icons that your application may use.
#### 3. `src/scenes/chatbot.jsx` holds the actual chatbot component and API calls to our backend.
#### 4. `src/App.js` is the central component of our application. It serves as the entry point to the UI. We import and load the chatbot component here.
#### 5. `src/index.js` is responsible for rendering the central component (App.js) into the DOM.
#### 6. `package.md` contains information on dependencies, scripts, configurations, and other metadata for our application.
#### 7. `package-lock.md` is automatically generated based on `package.md` whenever you modify your application dependencies (`npm install` or `npm update` a package).

        
## Running the Application
Once you have the prerequisites complete, environment variables set, and python environment activated, we can run the application.

### 1. Open a terminal. cd into Lab4\backend and run the following command:
```
C:\path\to\backend> python app.py
```

This will start our Flask API service on port 5000 so that our frontend can connect to the backend.

### 2. Open another terminal and cd into the `/ai-quickstart/Lab4/chatbot-ui` folder

>The frontend we have made for this application utilizes the [Cigna Canvas styling library](https://canvas-dev.cignacloud.com/getting-started). 

Run the following two commands to install the required packages and start the React frontend on localhost port 3000:

```
C:\path\to\chatbot-ui> npm install
C:\path\to\chatbot-ui> npm start
```

>NOTE: If you get an error when running ```npm install``` regarding a failure to find the @cigna/canvas package, run the following and try to install again:
```
C:\path\to\chatbot-ui> npm config set registry http://repo.sys.cigna.com/artifactory/api/npm/npm-repos
```

You now have a full-stack RAG AI chatbot running on your local machine! However, there is a large security risk in the application...

**Answer questions 1-2 in ```LAB_4_QUESTIONS.md```.**

Congratulations! You have completed Lab 4 of the AI Technologist Course. Follow the instructions in ai-quickstart/README.md to publish your labs to GitHub for review. Return to the content in myUniversity to continue the course.

