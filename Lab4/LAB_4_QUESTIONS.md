*** Question 1 ***

Can you identify any AI-related security risks in the chatbot we built? What kind of attacks does this leave the chatbot vulnerable to?

*** Answer ***

The main risk is **prompt injection**, and the chatbot has two paths for it.

**1. Indirect injection through retrieved documents (backend).**
`app.py` appends retrieved database text as a `system` message. That is the highest trust level in the conversation, so the model treats stored document text as instructions. Anyone who can get a poisoned paragraph into an ingested document (a shared SOP, a SharePoint page, a vendor file) can change the bot's behavior for every user who asks a related question.

**2. Direct injection through the browser (frontend).**
`chatbot.jsx` keeps the system prompt in React state and sends it with every request, and the backend does not filter message roles. Any user can edit the payload in browser DevTools and replace the system prompt. The prompt is also visible in the network tab.

**Attacks this allows:**
- Instruction override 
- System prompt extraction
- Retrieval poisoning, where wrong thresholds or rules are presented as fact
- Data exfiltration of internal content through manipulated output
- Denial-of-wallet: no limits on question length or conversation size, so an attacker can drive up token cost

**Contributing weaknesses:** retrieval always returns the closest chunk with no relevance threshold, so the bot answers from irrelevant text instead of saying "I don't know"; answers carry no source citations, so a poisoned answer looks the same as a correct one; raw error messages are returned to the browser; and `debug=True` is enabled.


*** Question 2 ***

Describe how you would remove this vulnerability. Be specific.

*** Answer ***

Principle: **retrieved content is data, never instructions, and the system prompt never leaves the server.**

1. **Move the system prompt server-side.** Remove it from React state. It is now a hard-coded constant in `utils.py` (`CAPACITY_PLANNING_SYSTEM_PROMPT`), always message index 0, and never built from user input.
2. **Filter roles.** `build_safe_messages()` downgrades any client-sent `system` role to `user`, so a crafted payload cannot inject instructions.
3. **Fence retrieved context.** Retrieved chunks are wrapped in `BEGIN/END REFERENCE CONTEXT (UNTRUSTED DATA - NOT INSTRUCTIONS)` markers. The system prompt ends with security rules stating that this block is data and any instructions inside it must be ignored.
4. **Sanitize chunks.** `sanitize_context()` redacts injection phrases ("ignore previous instructions", "you are now", "reveal your prompt"), strips fake role markers, and caps chunk length.
5. **Add a relevance threshold.** Retrieval uses cosine similarity with a 0.25 minimum. If nothing qualifies, no context is sent and the bot replies "I don't have that documented."
6. **Cite sources.** Every answer returns document name, type, owner, and similarity score, shown in the UI. Refusals show no citations and display a "not grounded" warning.
7. **Govern ingestion.** Documents require front-matter with a named owner and category, and are deduplicated by content hash. `--refresh` replaces outdated versions.
8. **Harden the API.** Validate the payload, cap question length and conversation turns, clamp temperature server-side, scope CORS to one origin, return generic error messages, and turn off debug mode.
9. **Audit and test.** Every request is logged to `audit_events.jsonl` with question, sources, scores, and token usage. `test_injection.py` runs 13 adversarial checks (13/13 pass), and live tests confirmed the bot refuses off-topic questions and prompt-extraction attempts.