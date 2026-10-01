# Risk Register

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| 1 | Extractor invents owners or quotes not in the transcript | High | High | Nullable owner in schema; prompt says null if unstated; code verifies every source quote appears in the transcript; track invented-owner count as a metric |
| 2 | Extractor is too cautious and misses real decisions (low recall) | Medium | High | Track precision and recall together; add few-shot examples for indirect phrasing; review every miss in the eval set |
| 3 | Eval set too small or unrealistic | Medium | High | Build it in Sprint 1, before RAG; 15 varied transcripts including hard cases (hedged decisions, conditions, unlabeled text) |
| 4 | Scope creep (audio, accounts, integrations) | High | Medium | Out-of-scope list in the charter; stretch goals locked until all Must stories are done; re-read charter at each sprint start |
| 5 | Retrieval returns text from the wrong meeting | Medium | High | Store meeting name and date as metadata; chunk by speaker turn with overlap; require citations; test with 20 questions |
| 6 | API key leaked or API costs spike | Low | High | Keys only in .env (gitignored); never pasted into chat; spending limit set on the OpenAI account; parser tests never call the API |
| 7 | Coursework competes for time | High | Medium | Protect a daily block; use the buffer week; cut Should and Could stories first |
