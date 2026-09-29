*** Question 1 ***

We created an embedding of some natural language information via the LLM. What is an embedding and what does it represent in the context of natural language processing?

*** Answer ***

An embedding is a numerical representation of text — a fixed-length list of numbers (in this lab, 1,536 values) that captures the *meaning* of a piece of content rather than just its literal words. In my project capacity inventory system context, the manager can ask a question in their own words and still retrieve the right spec, policy, or KPI definition. It turns unstructured documents (spec sheets, manager guides, procedure notes) into something the system can compare and rank by meaning — the foundation for semantic search across enterprise knowledge.

*** Question 2 ***

What are the reasons for implementing a RAG model into your application? Give an example use-case in your response.

*** Answer ***

- **Accuracy & trust:** answers are grounded in approved source documents, and
  can cite which document was used, so results are auditable.
- **Reduced hallucination:** the model answers from retrieved facts instead of
  guessing.
- **No retraining:** updating a document instantly updates the
  answers — no expensive model retraining required.
- **Security & governance:** sensitive data stays in controlled database
  rather than being baked into a public model.

use-case: An **Inventory / Capacity-Planning Knowledge Assistant**.
Instead of digging through Word docs and SharePoint pages to recall "how is
SITE_NM derived when the LAN_ID isn't in the map?", a manager asks the question
in plain English. The assistant retrieves the relevant spec, answers precisely,
and shows the source spec_id — saving analyst time and reducing inconsistent
answers across the team.

*** Question 3 ***

Explain the steps we used to implement context retrieval into our simple chatbot (basic_RAG.py).

*** Answer ***

The chatbot follows a clear retrieve-then-generate pattern:

1. **Capture the question** — the user types a prompt in the chat loop.
2. **Embed the question** — call `basic_embedding_generator()` to convert the question into the same 1,536-dimension vector format used for stored data, so the two can be compared mathematically.
3. **Similarity search** — pass that vector to `get_embedding_from_postgres()`, which uses Euclidean (L2) distance in the pgvector database to find the stored text whose meaning is closest to the    question, and returns that text as context.
4. **Assemble the prompt** — append the user's message to the conversation, then build a temporary conversation that also includes the retrieved context as a system message (kept temporary so the running history doesn't grow past the model's context limit).
5. **Generate the answer** — send that context-enriched conversation to `basic_chat_completion()`, print the response, and store the assistant's reply in the permanent history for continuity.

*** Question 4 ***

Describe some of the areas in the RAG pipeline that you can improve to increase the relevance and overall performance of the model.

*** Answer ***
using Capacity inventory system as the example to strengh the following stages:

- **Smarter chunking:** split documents along paragraphs or logical sections
  instead of a blind character count, so related information stays together and
  retrieval returns cleaner, more complete answers.
- **Retrieve multiple results (Top-K) + re-ranking:** pull the best 3–5 chunks
  rather than just one, then re-rank them, so complex questions that span
  several specs are answered fully.
- **Metadata filtering:** tag content by category, client, site, or effective
  date so a query can be scoped (e.g., only "CASH" specs), improving precision
  and enforcing access boundaries.
- **Hybrid search:** combine semantic (meaning) search with keyword search to
  reliably catch exact identifiers like `CLIENT_ID` or `RT_LN_ID`.
- **Better preprocessing/normalization:** clean and standardize text before
  embedding for higher-quality vectors.
- **Grounding guardrails & citations:** instruct the model to say "not found in
  the specs" instead of guessing, and show sources — essential for auditability
  and compliance.
- **Higher-quality embedding/chat models and caching:** improve accuracy and
  reduce cost/latency for frequently asked questions.

**************