# E-Commerce Support Agent — 5 Test Cases

Each test case maps to one of the four scenarios and validates the expected flow and outcome.

---

## Test Case 1 — Scenario 1: Policy Document Answers (Normal Operations)

**Scenario:** Customer asks a question related to normal operations; a policy document can be referred to and the user is satisfied with the answer.

### User Query

> "What is your return window? How many days do I have to return an item?"

### Expected Flow

1. **Ingestion** → Normalize query; extract priority, customer context.
2. **Planner** → Plan: Intent → RAG + Memory (parallel) → Reasoning → Response → Guardrails.
3. **Intent** → Classify: e.g., "returns", "policy", urgency P3.
4. **RAG** → Query vector store; retrieve chunks from **returns-refund-policy** (e.g., "30 days", "within 30 days of delivery").
5. **Memory** → Optional; may not find a closer match than RAG.
6. **Reasoning** → Prefer RAG policy content; correlate with intent.
7. **Response** → Synthesize answer citing policy: e.g., "Items may be returned within **30 days** of delivery for a full refund..."
8. **Guardrails** → Safety and confidence check pass (response references policy).
9. **Outcome** → Final response to user; no escalation.

### Expected Outcome

- User receives a clear answer stating the **30-day return window** (and optionally condition: unused, original packaging, proof of purchase).
- Source cited: Returns and Refund Policy (POL-RET-001) or equivalent.
- No ticket created; no escalation.

### Training Doc Reference

- **Policy:** `training-docs/policies/returns-refund-policy.md` — Section 1 (Return Eligibility): "within **30 days** of delivery."

---

## Test Case 2 — Scenario 2: Policy Does Not Have Answer; FAQ Has Answer

**Scenario:** The policy document does not have the answer, but the FAQ has the answer.

### User Query

> "Why is my coupon code not working at checkout? I have a screenshot of the banner and my cart meets the minimum."

### Expected Flow

1. **Ingestion** → Normalize query (coupon, checkout).
2. **Intent** → Classify: e.g., "promotions", "checkout", "coupon".
3. **RAG** → Query vector store; policy docs may have weak or no match; **FAQ** chunks (e.g., "Why is my coupon code not working at checkout?") should be retrieved with higher relevance.
4. **Reasoning** → Use FAQ content: common reasons (expired, minimum not met, case-sensitive, combination rules) and "contact support with code and screenshot; we can verify and apply manually if valid."
5. **Response** → Synthesize answer from FAQ: explain possible reasons and next step (contact support with code and screenshot for manual verification).
6. **Guardrails** → Pass (response references retrieved FAQ).
7. **Outcome** → User satisfied with answer; no escalation.

### Expected Outcome

- User receives an answer explaining **why coupon codes might not work** (expiry, minimum, case-sensitive, combination rules) and that they can **contact support with the code and screenshot** for manual verification if valid.
- Source: FAQ (ecommerce-faq.md), not policy.
- No ticket created; no escalation.

### Training Doc Reference

- **FAQ:** `training-docs/faqs/ecommerce-faq.md` — "Why is my coupon code not working at checkout?"

---

## Test Case 3 — Scenario 3: RAG Cannot Satisfy; Memory Agent Solves the Problem

**Scenario:** The existing RAG knowledge base (policies + FAQs) cannot fully satisfy the answer, but based on the Memory agent's capability, the Memory agent helps solve the problem (past similar incident).

### User Query

> "I was charged twice for the same order when I clicked Place Order twice because the page was slow. Can you refund one of the charges?"

### Expected Flow

1. **Ingestion** → Normalize (duplicate charge, refund request).
2. **Intent** → Classify: e.g., "payment", "refund", "duplicate charge".
3. **RAG** → Query vector store; policies/FAQs may mention "refund" or "payment" but not this specific **duplicate-charge-due-to-double-submit** scenario with resolution.
4. **Memory** → Search episodic memory; find **INC-2025-001** (or similar): "Customer was charged twice for the same order when they clicked Place Order twice... Refunded the duplicate order in full..."
5. **Reasoning** → RAG insufficient; use Memory resolution: verify duplicate (same cart, same payment, within short time), refund duplicate, advise to wait for confirmation.
6. **Response** → Synthesize: "We can help. In similar cases we verify the duplicate order and refund the duplicate in full. Please provide your order number (or the one you want to keep) and we'll process the refund for the duplicate. We also recommend waiting for the order confirmation before refreshing to avoid double submission."
7. **Guardrails** → Pass (response references past resolution / memory).
8. **Outcome** → User satisfied; no escalation (or follow-up human step only if needed for actual refund execution).

### Expected Outcome

- User receives a **resolution path** that matches the **past incident** (INC-2025-001): verify duplicate, refund duplicate, and practical advice.
- Source: Memory agent (Episodic Memory) — past-resolved-incidents.json, incident_id INC-2025-001.
- No escalation required for answering; actual refund may be automated or require human execution depending on implementation.

### Training Doc Reference

- **Memory:** `training-docs/memory-agent-scenarios/past-resolved-incidents.json` — `INC-2025-001` (duplicate charge, double submit, refund duplicate).

---

## Test Case 4 — Scenario 4: RAG and Memory Cannot Solve; Escalate to Human (Ticket in Database)

**Scenario:** Both RAG and Memory agent could not solve the problem; the issue is escalated to HUMAN via creation of a ticket in the database.

### User Query

> "I need a bulk quote for 50,000 units with custom branding and net-60 payment terms for my company. Who can I talk to?"

### Expected Flow

1. **Ingestion** → Normalize (bulk, quote, custom, B2B).
2. **Intent** → Classify: e.g., "sales", "B2B", "custom order", "quote".
3. **RAG** → Query vector store; policies and FAQs do not cover **bulk quotes**, **custom branding**, or **net-60 payment terms**.
4. **Memory** → Search episodic memory; no similar past incident (no bulk/custom/Net-60 resolution).
5. **Reasoning** → No confident answer from RAG or Memory; recommend escalation.
6. **Response** → May still generate a polite response: "This type of request (bulk quote, custom branding, net-60 terms) is handled by our sales team. We're creating a ticket and a specialist will contact you."
7. **Guardrails** → **Escalation criteria met**: query outside knowledge base, complex B2B request; confidence below threshold or policy triggers human handoff.
8. **Escalation** → Create **ticket** in application database (PostgreSQL); status e.g. `open` or `escalated`; priority as per policy (e.g. P2 for B2B).
9. **Outcome** → User is informed that a ticket has been created and a human/sales will follow up.

### Expected Outcome

- User is told that their request is being **escalated** and that a specialist (sales) will contact them.
- A **ticket** is created in the application database with:
  - **Title:** e.g. "Bulk quote request: 50,000 units, custom branding, net-60 payment terms"
  - **Description:** User query or summarized context
  - **Status:** `open` or `escalated`
  - **Priority:** e.g. P2 (or as per escalation policy)
- No automated resolution from RAG or Memory; human handoff is the resolution path.

### Verification

- Query the **tickets** table in PostgreSQL (or via TicketService) and confirm a new row with the above characteristics.
- Optional: Verify that observability/logging recorded the escalation and ticket creation.

---

## Test Case 5 — Scenario 1: Policy Document Answers (Refund Processing Time)

**Scenario:** Customer asks a question related to normal operations; a policy document can be referred to and the user is satisfied with the answer.

### User Query

> "How long does it take to get my refund after I return an item?"

### Expected Flow

1. **Ingestion** → Normalize (refund, timing, returns).
2. **Intent** → Classify: e.g., "refunds", "policy", "timeline".
3. **RAG** → Query vector store; retrieve chunks from **returns-refund-policy** (e.g., "inspect and notify within 5 business days," "refund processed within 7 business days").
4. **Reasoning** → Use policy: 5 business days for approval/rejection notice, 7 business days for refund to payment method.
5. **Response** → Synthesize: "Once we receive your return, we'll inspect it and notify you within **5 business days**. If approved, your refund will be processed within **7 business days** to your original payment method."
6. **Guardrails** → Pass (response references policy).
7. **Outcome** → Final response to user; no escalation.

### Expected Outcome

- User receives a clear answer: **5 business days** for inspection/notification, **7 business days** for refund to payment method.
- Source: Returns and Refund Policy (POL-RET-001) — Section 2 (Refund Processing).
- No ticket created; no escalation.

### Training Doc Reference

- **Policy:** `training-docs/policies/returns-refund-policy.md` — Section 2 (Refund Processing).

---

## Summary Table

| Test Case | Scenario | User Query (summary)           | Primary source        | Escalation? |
|-----------|----------|--------------------------------|------------------------|-------------|
| 1         | 1        | Return window (days)           | Policy (returns)       | No          |
| 2         | 2        | Coupon not working             | FAQ                    | No          |
| 3         | 3        | Duplicate charge (double submit)| Memory (INC-2025-001) | No          |
| 4         | 4        | Bulk quote, custom, net-60     | None                   | Yes (ticket)|
| 5         | 1        | Refund processing time         | Policy (returns)       | No          |
