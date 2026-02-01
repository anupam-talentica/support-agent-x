# 15-Minute Demo — Key Areas & Timestamps

| Time         | Section             | What to cover                                                                                                                                                                                                                                   |
| ------------ | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0:00–0:45   | Intro & problem     | Pitch: multi-agent e-commerce support; pain (scale, escalation); <br />solution: 8 agents, A2A, RAG, memory, guardrails.                                                                                                                        |
| 0:45–2:30   | Architecture        | 8 agents (Ingestion→Planner→Intent→RAG+Memory→Reasoning→Response→Guardrails). <br />3 stores: PostgreSQL, ChromaDB, SQLite+mem0. Host orchestrates; React UI→Host via API/SSE.                                                           |
| 2:30–4:00   | Setup               | `docker-compose up --build`, `.env` (API keys), ChromaDB + ingest. UI: localhost:12000, Host: 8083.                                                                                                                                         |
| 4:00–9:30   | Live demo — Chat   | React UI + TEST_CASES-style queries; show SSE status.<br /> 1) Policy: return window → RAG.<br /> 2) FAQ: coupon not working → RAG. <br />3) Memory: charged twice → past incident. <br />4) Escalation: bulk quote → ticket in PostgreSQL. |
| 9:30–11:00  | Flow under the hood | Pipeline: Ingestion→Planner→Intent→RAG+Memory→Reasoning→Response→Guardrails. <br />Guardrails can create ticket when unsolved.                                                                                                            |
| 11:00–12:00 | Observability       | Langfuse trace (Ingestion→…→Response);`X-User-Phone` for user tracing. Or one line: traces → Langfuse.                                                                                                                                    |
| 12:00–13:30 | Data & training     | Policies, FAQs, past incidents (mem0). RAG ingest + memory seed for duplicate-charge case.                                                                                                                                                      |
| 13:30–14:30 | Codebase            | Tour:`agents/`, `react-ui/`, `database/`, `docker-compose.yml`. Add agents via A2A; Host discovers by URL.                                                                                                                              |
| 14:30–15:00 | Wrap-up             | Recap: multi-agent, policy+FAQ+memory+escalation, one-command run, observability. Repo/README; Q&A.                                                                                                                                             |

---

## Notes for your review

- **Adjust time per scenario** (e.g. spend more on Memory + Escalation if that's your differentiator).
- **Observability**: Expand to ~1:30 if you want a short Langfuse walkthrough; keep at ~0:30 if you only mention it.
- **Setup**: If you skip "from scratch" and start from an already-running stack, you can shave ~0:30–1:00 and give it to the live demo or architecture.
- **Optional**: Add a 30-second "Admin / Dashboard" moment (e.g. AdminQueries or ticket list) if you have a screen that adds value.

---

*When you've edited the timestamps and sections, use the same outline to create the detailed voiceover script.*
