# Testing Documents for E-Commerce Support Agent

This folder contains **test cases** for validating the support agent flow across four scenarios:

| Scenario | Description | Expected behavior |
|----------|-------------|-------------------|
| **Scenario 1** | Customer asks a question related to normal operations; a **policy document** can be referred to and the user is satisfied with the answer. | RAG retrieves policy → Reasoning/Response use it → Guardrails pass → Final response to user. |
| **Scenario 2** | The policy document does **not** have the answer, but the **FAQ** has the answer. | RAG retrieves FAQ (not policy) → User is satisfied with answer. |
| **Scenario 3** | RAG knowledge base (policies + FAQs) **cannot** satisfy the query, but the **Memory agent** (past resolved incidents) helps solve the problem. | RAG returns low relevance or no match → Memory agent finds similar past incident → Reasoning/Response use memory resolution → User satisfied. |
| **Scenario 4** | Both RAG and Memory agent **cannot** solve the problem → issue is **escalated to HUMAN** via creation of a **ticket in the database**. | RAG and Memory both fail or confidence < threshold → Guardrails trigger escalation → Ticket created in application DB (PostgreSQL) → User informed of escalation. |

## Test Cases

See **TEST_CASES.md** for the five test cases:

1. **Test Case 1** — Scenario 1: Policy-based (return window).
2. **Test Case 2** — Scenario 2: FAQ-based (coupon not working).
3. **Test Case 3** — Scenario 3: Memory-based (duplicate charge, past incident).
4. **Test Case 4** — Scenario 4: Escalation to human (ticket created).
5. **Test Case 5** — Scenario 1: Policy-based (refund processing time).

## Prerequisites

- **Training docs** are ingested:
  - `training-docs/policies/*` and `training-docs/faqs/*` are in the RAG vector store (ChromaDB).
  - `training-docs/memory-agent-scenarios/past-resolved-incidents.json` is loaded into the Memory agent's Episodic Memory (SQLite).
- Application database (PostgreSQL) is running and tickets table is available for Scenario 4.
- All agents (Host, Planner, RAG, Memory, Reasoning, Response, Guardrails, etc.) are running per HACKATHON_PLAN.md.

## How to Run

1. Ingest training documents into RAG and Memory (see `training-docs/README.md`).
2. Start the support agent stack (Host, agents, UI).
3. For each test case in **TEST_CASES.md**, submit the given **User Query** via the support chat/ticket UI.
4. Verify **Expected Flow** and **Expected Outcome** (including ticket creation for Test Case 4).
5. For Test Case 4, verify in the application database that a new ticket was created with the expected title/description and status (e.g., `open` or `escalated`).
