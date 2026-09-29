*** Question 1 ***

Can you identify any AI-related security risks in the chatbot we built? What kind of attacks does this leave the chatbot vulnerable to?

*** Answer ***

The largest security risk is Prompt Injection. The application directly appends retrieved database content into the model's conversation as a system message without validating or filtering it.

A malicious document could instruct the model to ignore previous guidance, reveal internal information, or provide inaccurate responses. Because the retrieved content is automatically inserted into the prompt, the model cannot reliably distinguish trusted instructions from untrusted retrieved documents.

This could expose confidential company information, return inaccurate policy guidance, or cause users to trust manipulated responses.

*** Question 2 ***

Describe how you would remove this vulnerability. Be specific.

*** Answer ***

To remove this vulnerability, retrieved documents should never be inserted as trusted system instructions. Instead, retrieved content should be clearly separated from system prompts and treated only as reference material.

Access controls should restrict what documents may be indexed, and retrieved responses should include citations so users can verify the information source.

These controls reduce the risk of confidential data exposure, improve trustworthiness of AI-generated responses, and ensure company policies and procedures cannot be overridden by malicious or inaccurate documents.

**************

