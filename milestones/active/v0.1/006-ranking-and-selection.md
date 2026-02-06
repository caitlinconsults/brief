# Ranking and Selection -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A scoring engine that ranks enriched content items and selects the top items per topic cluster per lane for inclusion in the daily digest. This determines what the user actually sees.

**TO WHOM**: The user, whose time and attention are the scarcest resources. A bad ranker means the user reads noise; a good ranker means every item earns its spot.

**WHY**: 20 sources will produce far more content daily than anyone can or should read. Ranking is the editorial judgment layer — it decides "of everything that happened today in AI, these are the 15-25 things that matter to you, and here's why."

## Requirements

### Scoring
- Each item receives a composite relevance score based on:
  - **Recency**: More recent content scores higher, with decay
  - **Source trust weight**: From the source registry (spec 001)
  - **Lane affinity**: How strongly the item matches each lane (spec 004)
  - **Popularity signals**: Where available (e.g., HN score/comments, social engagement)
  - **Novelty**: Genuinely new developments score higher than continuing coverage of known stories
  - **User feedback history**: Items similar to past "more like this" signals score higher; items similar to "less like this" score lower

### Selection
- For each topic cluster, select the top N items per relevant lane
- Not every cluster will have items in all three lanes — that's expected
- Include a "novelty budget": ~20-30% of selected items should be adjacent or exploratory (things the user might not expect but should see) to prevent filter bubble effects
- Target total digest size: 15-25 items across all clusters and lanes (configurable)

## Requirements (behavioral)

- Ranking is deterministic given the same inputs (no randomness in scoring, only in novelty slot selection)
- Ranking runs after enrichment, as part of the same daily pipeline
- The ranker does not use an LLM — scoring and selection are rule-based and deterministic
- Scoring weights are configurable without code changes

## Deferred to Post-MVP

- **Feedback integration**: User feedback ("more like this", "less like this", "too technical", "too fluffy") adjusting future scoring. The schema stores feedback fields (spec 002), but the ranking engine doesn't consume them yet. This gets added once the feedback collection mechanism is built in a future milestone.

## Success Criteria

- [ ] Items are scored and the top items per cluster per lane are selected
- [ ] Total digest size stays within the 15-25 item target range
- [ ] Novelty budget is respected (~20-30% of items are exploratory)
- [ ] Scoring weights can be adjusted via configuration
