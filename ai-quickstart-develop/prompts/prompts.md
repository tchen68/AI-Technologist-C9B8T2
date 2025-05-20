# Prompting Tips & Techniques

## Techniques

### One-Shot Prompting
One example is given with the query to reduce hallucinations in the response.

This is useful for when there's a specific format/type of response you need.

### Few-Shot Prompting
Multiple examples are given with the query to reduce hallucinations and cover a broad range of domains or sub-domains.

This is preferred over one-shot when you have more complex queries that may involve information from various sources.

### Chain-of-Thought
COT Prompting takes one or few-shot prompting and sends it in a Q&A format with the last answer left blank for the LLM to fill in with it's response. This guides its reasoning better.

> Basic Format Example:
Think step-by-step.
Q: The sun has been out all day. Will it be wet outside?
A: Even if it rained before, it is probably dry outside by now.
Q: It rained all night and it's cloudy now today. Will it be wet outside?
A:

## Tips
### Prompt Structure
1. Provide the most important context of your query at the beginning and/or end of the prompt. LLM attention tends to capture this more.

2. Guide the LLM through the prompt. Use words like "think through" and "step by step" to make it break down the question and reason better.

3. For longer queries, chunk out sections and label them. For example, you could use headers such as **"INTRODUCTION"**,**"EXAMPLES"**, and **"ADDITIONAL INFO"**.

4. Although enforcing json structures is a feature provided by OpenAI, if there's other formats that you want to receive the output as, you can include lines such as:

- "Your answer must be in the following format: {your format}. Do not respond in any other format. Only output this final formatted object"

### Prompt Information & Personification
1. For better breakdowns, details, or explanations, ask the LLM to:

- "explain as if I'm an introductory student to {your topic}"
- "break down your response as if I'm an expert programmer"
- "I am a nurse practioner with over 10 years of experience. Provide me a detailed & informative response regarding {your topic}

2. Use one-shot or few-shot prompting. This means you provide an example(s) of responses you would expect for a similar type of query, helping guide the LLM to respond back similarly.

- Provide a synthetic claim example with your question
- Give a simulated case example of a patient visit along with your question

### Prompts w/ Chat or Q&A
1. Reset the LLMs behavior with phrases like:
- "You must respond with..."
- "From now on, you will {LLM behavior} when I talk to you"
- "You are an expert programmer and can solve any problem given to you. Please provide code for {your task}"

### Combining Together w/ CO-STAR

The CO-STAR method combines all of these tips in the following way:

*C - Context:* Provide all the information about the task/query asked.

*O - Objective:* Define the goal of the task and what the end result of your query is.

*S - Style:* The way the LLM responds (person / skill level it emulates)

*T - Tone:* Similar to style, the speech style of the response.

*A - Audience:* Explain who the response is for / who the query is being made by.

*R - Response:* Provide the actual response format and structure that you want.