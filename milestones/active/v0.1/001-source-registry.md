# Source Registry -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A single file that lists all 20 content sources and their settings — how to fetch them, how often, how much to trust them, and which lane(s) they belong to. You open this file, you see your sources, you edit it to add or change one. The pipeline reads this file to know where to go get content.

**TO WHOM**: You, as the person curating your own information diet. You should be able to open this file, understand it immediately, and make changes without touching any pipeline code.

**WHY**: Sources are the foundation. If the sources are wrong, everything downstream is garbage. Keeping them in one readable file means you can swap sources, adjust trust weights, or disable something that's gotten noisy — all without re-engineering the pipeline.

## The 20 Sources

Organized by lane affinity (a source can feed multiple lanes):

### Builders Lane (7 sources)
1. **Hacker News** — Early-warning system for real projects. API available.
2. **Latent Space** — Agent frameworks, orchestration, evals, production writeups.
3. **Simon Willison's Weblog** — New AI tools explained through concrete experiments.
4. **OpenPipe** — Agent deployment, fine-tuning, production lessons.
5. **LangChain Blog** — Patterns emerging across real users and enterprise.
6. **Lilian Weng Blog** — Agents, memory, planning, failure modes.
7. **Indie Hackers** — Who is actually charging money for AI tools right now.

### Product & Spec Thinking (5 sources)
8. **Shreyas Doshi Newsletter** — Translating ambiguous ideas into crisp specs.
9. **Lenny's Newsletter** — How AI features get prioritized, tested, shipped, sold.
10. **Not Boring** — Where AI products fit into market structure.
11. **a16z Blog** — Infrastructure, enterprise, workflow automation analysis.
12. **Y Combinator Blog** — AI-first startups before they're widely known.

### Security Lane (4 sources)
13. **OWASP AI/LLM Top 10** — Practical threat modeling for prompt injection, data leakage, agent abuse.
14. **AI Incident Database** — Concrete failure cases, not hypotheticals.
15. **Anthropic Safety Blog** — Alignment, misuse, deployment risk.
16. **Trail of Bits Blog** — AI security explained for strategists and execs.

### Business Lane (4 sources)
17. **McKinsey AI Insights** — Where AI moves metrics and where it doesn't.
18. **Bain AI Brief** — Operating models, org design, ROI language.
19. **Stripe Sessions** — Real companies explaining real systems.
20. **Salesforce Engineering Blog** — Large-scale AI deployments with real constraints.

## What This Actually Is

A single config file that lives in the project folder. Not a database, not a UI — just a readable text file. Each source entry includes:

- **Name**: e.g., "Hacker News"
- **Fetch method**: How the pipeline gets content from it — RSS feed, API call, or web scrape
- **Lane(s)**: Which digest lane(s) this source feeds (Builders, Security, Business — can be more than one)
- **Trust weight**: How much to trust this source when ranking (scale of 0.0–1.0; higher = more influential in the digest)
- **Fetch cadence**: How often to check for new content (hourly, daily, weekly)
- **Enabled/disabled**: A toggle so you can turn a source off without deleting it

## MVP Approach

For the initial build, only **Simon Willison's Weblog** is enabled. It was chosen because:
- Clean, well-maintained RSS feed (just works)
- Single author, no user-submitted content (lowest prompt injection risk in the entire source list)
- Updates frequently with exactly the kind of AI builder content we care about

The remaining 19 sources are defined in the file but marked as disabled. They get enabled incrementally once the pipeline is proven end-to-end. Hacker News is intentionally saved for later — it's user-submitted content with comments, making it the highest prompt injection risk in the source list.

## Source Accessibility Audit

Not all 20 sources have clean RSS feeds or APIs. Here's what we know (feed URLs need live verification at build time):

### EASY — 8 sources (clean RSS or API, wire up immediately)
| Source | How to fetch | Notes |
|--------|-------------|-------|
| Hacker News | RSS (`/rss`) + Firebase API (no auth) | API gives top/new/best stories + individual items |
| Simon Willison's Weblog | Atom feed (`/atom/everything/`) + Datasette JSON API | Unusually rich access — the best source on this list for programmatic data |
| Latent Space | Substack RSS (`/feed`) | Some posts are paywalled; titles + excerpts still available for all |
| LangChain Blog | Ghost CMS RSS (`/rss/`) | Full-content feed, no paywall |
| Lilian Weng Blog | Hugo RSS (`/index.xml`) | Low volume (monthly-ish) but very high quality |
| Shreyas Doshi Newsletter | Substack RSS (`/feed`) | Some paid posts; titles + excerpts available for all |
| Not Boring | Substack RSS (`/feed`) | Good free-to-paid ratio |
| Trail of Bits Blog | WordPress RSS (`/feed/`) | Standard WordPress, fully open |

### MODERATE — 5 sources (likely accessible but needs verification)
| Source | How to fetch | Notes |
|--------|-------------|-------|
| Lenny's Newsletter | Substack RSS (`/feed`) | **Heavy paywall** — most content is paid. Titles + excerpts only for paid posts. Good enough for "what's being discussed" but not deep summarization |
| a16z Blog | Likely WordPress RSS (`/feed/`) | Site has been redesigned multiple times; feed URL needs verification |
| Y Combinator Blog | Likely RSS | Site recently redesigned; feed URL needs verification |
| AI Incident Database | Likely has a GraphQL API | Structured database of incidents, not a content feed — needs custom query for "recently added" |
| Salesforce Engineering Blog | Likely Medium RSS | May have migrated off Medium; verify at build time |

### HARD — 7 sources (no feed, scraping required, or not really a content source)
| Source | Problem | Recommendation |
|--------|---------|---------------|
| OpenPipe Blog | Next.js site, no confirmed RSS | Build a scraper (low volume, manageable) |
| Indie Hackers | Forum format, uncertain feed, site direction unstable since Stripe acquisition | **Consider replacing** — poor signal-to-noise for automated ingestion |
| OWASP AI/LLM Top 10 | **Not a content feed** — it's a reference document that updates infrequently | Monitor the GitHub repo via API for releases; change fetch cadence to weekly/monthly |
| Anthropic Safety Blog | Modern corporate website, no confirmed RSS | Build a scraper (low volume, high signal — worth it) |
| McKinsey AI Insights | Enterprise website with aggressive bot protection (Akamai/Cloudflare) | **Hardest source on the list.** Consider subscribing to their email newsletter and ingesting from inbox instead, or replacing |
| Bain AI Brief | Enterprise website with bot protection | Same problem as McKinsey — consider email newsletter or replacing |
| Stripe Sessions | **Not a content feed** — it's a conference/event series | Redefine as "Stripe Blog" and verify if blog RSS exists; event content is episodic, not daily |

### Recommended Enable Order (after Simon Willison MVP)
1. **Phase 1**: Enable all 8 EASY sources (just RSS parsing, minimal effort)
2. **Phase 2**: Verify and enable MODERATE sources (quick feed URL checks)
3. **Phase 3**: Build scrapers for high-value HARD sources (OpenPipe, Anthropic)
4. **Phase 4**: Decide whether to replace or rework the remaining HARD sources (McKinsey, Bain, Indie Hackers, OWASP, Stripe)

Sources flagged as HARD don't block the MVP — the pipeline is proven with EASY sources first.

## Requirements

- All 20 sources are listed in one file with the fields above
- Adding a new source means editing this file — no code changes needed
- Disabling a source means flipping its toggle, not removing it
- The file is human-readable (you should be able to open it and understand it at a glance)
- MVP launches with only Simon Willison's Weblog enabled; others are present but disabled

## Success Criteria

- [ ] All 20 sources are defined with type, lane affinity, trust weight, and fetch cadence
- [ ] Simon Willison's Weblog is enabled; remaining 19 are present but disabled
- [ ] A source can be disabled and re-enabled via configuration
- [ ] A new source can be added by editing the configuration file alone
- [ ] Each source's fetch method is specified (RSS URL, API endpoint, or scrape target)
