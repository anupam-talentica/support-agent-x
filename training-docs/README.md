# Training Documents for E-Commerce Support Agent

This folder contains documents used to train and populate the support agent's knowledge bases:

- **policies/** — Official policy documents (ingested into RAG). Used when customer questions relate to normal operations and can be answered from policy.
- **faqs/** — Frequently Asked Questions (ingested into RAG). Used when the policy document does not contain the answer but the FAQ does.
- **memory-agent-scenarios/** — Past resolved incidents in episodic memory format. Fed to the Memory agent. Used when RAG (policies + FAQs) cannot satisfy the query but a similar past case was resolved and can be recalled by the Memory agent.

## Usage

1. **RAG ingestion**: Ingest contents of `policies/` and `faqs/` into the vector store (ChromaDB) so the RAG agent can retrieve them.
2. **Memory agent**: Load `memory-agent-scenarios/past-resolved-incidents.json` into Episodic Memory:
   - From `support_agents` root: `python scripts/seed_memory_episodic.py`
   - Ensures the Memory database is initialized first: `python agents/memory_agent/scripts/init_memory_db.py`

## Document Design

- Policy docs are written so that **Scenario 1** test cases can be answered from them.
- FAQs contain answers that are **not** duplicated in policy docs, so **Scenario 2** (policy fails, FAQ succeeds) can be tested.
- Memory scenarios describe resolutions that are **not** in policy or FAQ, so **Scenario 3** (RAG fails, Memory succeeds) can be tested.
