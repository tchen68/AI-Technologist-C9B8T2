*** Question 1 ***

How do we maintain the conversation history with the LLM in this lab?

*** Answer ***

The conversation history is maintained by storing all user prompts and assistant responses in the conversation object, this improves the user experience by reducing repetitive questions and enabling more intelligent interactions

*** Question 2 ***

What type of object is 'conversation'? Be specific.

*** Answer ***

system
user
assistant

This structure functions as the LLM's short-term memory. It enables AI assistants to maintain context throughout a  workflow.

*** Question 3 ***

Was the LLM able to convert its previous response to JSON format? Do you think any LLM will always generate perfectly formatted JSON? Why or why not? 

*** Answer ***

Yes, the LLM was generally able to convert its previous response into JSON format because it had access to the conversation history. However, LLMs do not always generate perfectly formatted JSON because they generate text probabilistically. Formatting mistakes, missing brackets, extra commas, or explanatory text outside the JSON structure can occur. Production applications often use structured output techniques or schema validation to ensure valid JSON.

*** Question 4 ***

Compare the responses you received when requesting a 5,000-word essay about the sky, a 100-word essay about the sky, and a 100-word essay about the sky again but with max_tokens=50. 

*** Answer ***

The 5,000-word essay request produced a significantly longer response and may have encountered output limits or response truncation due to token restrictions. Large outputs consume substantially more tokens and increase cost, latency, and resource usage.

The 100-word essay was completed successfully because the requested output length was well within the model's token limits.

When max_tokens=50 was added, the model was restricted to generating approximately 50 tokens, resulting in an incomplete or shortened essay. The response stopped even though the requested task was not fully completed.

From a business perspective, token management is important because it directly affects in response quality, API costs, Processing time, and User experience.

*** Question 5 ***

What differences do you notice in the two responses? How can we use temperature to our advantage when building out generative AI applications?

*** Answer ***

When the temperature was set to 0, the responses were more predictable, focused, and consistent. Repeating the same prompt typically resulted in very similar outputs.

When the temperature was increased to 1, the responses became more diverse, creative, and varied. The model explored different ideas and generated less predictable answers.

0.0 - Highly deterministic, Nearly identical results each time, uses for SQL generation, VBA code, data extraction, policy explanations
0.2 - Very consistent, Low variation, uses for Financial reporting, KPI summaries, operational documentation
0.5 - Balanced, Moderate variation, uses for Business communications, meeting summaries, project updates
0.7 - Creative, More diverse ideas, uses for Process improvement suggestions, workshop facilitation
1.0 - Highly creative, Significant variation, uses for Brainstorming, innovation sessions, marketing content

**************