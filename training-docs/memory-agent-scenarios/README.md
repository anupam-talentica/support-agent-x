# Memory Agent Scenarios (Episodic Memory)

This folder contains **past resolved incidents** that can be fed into the Memory agent's Episodic Memory. These scenarios are **intentionally not** covered in the policy documents or FAQ, so that:

- **Scenario 3** test cases can be satisfied by the Memory agent when RAG (policies + FAQs) does not have the answer.
- The Memory agent can recall similar past cases and suggest or apply the same resolution.

## Schema (Episodic Memory)

Each entry should align with the Memory agent's Episodic Memory schema:

- `incident_id`: Unique identifier
- `query_text`: Customer question or issue description (what they asked / what happened)
- `resolution`: What was done to resolve it
- `outcome`: `resolved`, `escalated`, or `pending`
- `tags`: List of tags for categorization (e.g., `["duplicate_charge", "refund", "EU"]`)
- `user_id`: Optional
- `timestamp`: When the incident occurred
- `metadata`: Optional extra context

## Usage

1. Load the JSON file into the Memory agent's SQLite database (Episodic Memory table).
2. Use the provided script or database tool to insert records from `past-resolved-incidents.json`.
3. When a customer asks something that RAG cannot answer, the Memory agent can search by `query_text` or tags and return the `resolution` from a similar past incident.

## Design Note

These scenarios describe **specific past cases** (e.g., "duplicate charge due to double submit," "wrong item to EU customer") so that:

- Test Case 3 can ask a question that matches one of these (e.g., "I was charged twice for the same order last month—can you help?") and the Memory agent can return the resolution (refund duplicate, etc.) even though the exact wording may not be in policy or FAQ in the same form.
