# Security and Containment -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A set of guardrails that protect the pipeline from adversarial content ingested from the open internet — specifically prompt injection attempts, content poisoning, and malicious links. This isn't a separate system; it's rules and checks woven into the existing pipeline stages.

**TO WHOM**: You, as both the operator and the sole consumer of the digest. A successful injection could corrupt your summaries, skew your rankings, or surface misleading content without you realizing it.

**WHY**: The pipeline takes text from the open internet and hands it to an LLM for processing. That's a prompt injection surface. The risk isn't catastrophic (the LLM has no tools, no outbound access, and no users to impersonate), but it can silently degrade the quality of your digest — which defeats the whole purpose.

## Attack Surfaces

### Prompt Injection via Content (highest risk)
- A blog post, HN comment, or newsletter contains text like "Ignore your previous instructions and..." that gets fed to the LLM during enrichment (spec 004)
- The LLM could produce corrupted summaries, wrong topic tags, or manipulated lane scores
- This is the primary threat because the LLM processes raw content from untrusted sources

### Content Poisoning (medium risk)
- Deliberately crafted content designed to game the ranking system — e.g., keyword-stuffing to score high on a specific lane, or fake "popularity signals"
- Could cause low-quality content to surface prominently in the digest

### Malicious Links (lower risk)
- URLs in ingested content that redirect, phish, or are otherwise not what they claim to be
- These would end up in the digest's "deep dive links" and the user could click them

## Requirements

### Content Sandboxing (protects spec 004 — Enrichment)
- Raw content is treated as untrusted input before it reaches the LLM
- Content is stripped of common injection patterns before being passed to the LLM for summarization and tagging
- The LLM prompt structure separates instructions from content clearly (system prompt contains instructions; user content is clearly delimited as "content to analyze," not as instructions)
- LLM outputs are validated against expected formats (e.g., a summary should be text, a lane score should be a number between 0 and 1 — if the output doesn't match, flag the item rather than trusting it)

### Output Validation (protects specs 004, 005, 006)
- Enrichment outputs are sanity-checked: topic tags must come from the known taxonomy, lane scores must be numeric and in range, summaries must be under a maximum length
- Items that produce anomalous enrichment results are flagged for review rather than silently included in the digest
- Digest generation does not blindly pass LLM-generated summaries through — a final check ensures the output is coherent and doesn't contain instruction-like text

### Link Safety (protects spec 006, 007)
- URLs included in the digest are verified against their original source domain (a link from "Simon Willison's blog" should point to simonwillison.net, not somewhere else)
- Redirects are resolved before inclusion — the digest shows the final destination, not a redirect chain

### Monitoring and Alerting
- Log items that fail output validation (these are potential injection attempts or content poisoning)
- Track anomaly rates per source — if a source suddenly produces a spike in flagged items, surface that in the pipeline run log
- No action is needed for low anomaly rates; this is about noticing if something changes

## What This Does NOT Cover (deferred)

- User authentication or access control (single-user MVP, no multi-tenancy)
- API key rotation or secrets management (handled at the infrastructure level, not the pipeline level)
- DDoS or abuse of the pipeline itself (not exposed to the internet)

## Success Criteria

- [ ] Raw content is clearly separated from LLM instructions in all prompts (no mixing of untrusted content with system instructions)
- [ ] LLM outputs are validated against expected formats before being stored
- [ ] Items that fail validation are flagged, not silently included in the digest
- [ ] URLs in the digest point to their claimed source domains
- [ ] Anomalous enrichment results are logged per source per run
- [ ] A known prompt injection string embedded in test content does not corrupt the summary or lane scores
