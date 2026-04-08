# Vault — Claude Code Operating Instructions

Vault is a personal knowledge engine. You (Claude Code) ingest raw sources and build a living, interlinked Obsidian wiki. The human curates sources; you read, summarize, cross-reference, and maintain the wiki. Full specs live in [[BRD]] and [[PRD]] — read them before any major operation.

---

## Directory Structure

```
vault/
├── CLAUDE.md              # This file — your operating instructions
├── index.md               # Wiki content catalog (you maintain this)
├── log.md                 # Chronological activity log (append-only)
├── raw/                   # Layer 1: Immutable raw sources (never modify)
│   ├── youtube/{Channel_Name}/   # Transcripts per channel
│   ├── articles/                 # Web articles as markdown
│   ├── pdfs/                     # PDF text extractions
│   └── ppts/                     # PPT text extractions
├── wiki/                  # Layer 2: LLM-generated wiki (you own this)
│   ├── sources/           # One summary per ingested source
│   ├── entities/          # People, companies, brands
│   ├── concepts/          # Recurring ideas, frameworks, metrics
│   ├── topics/            # Broader themes, industry verticals
│   ├── channels/          # YouTube channel overview pages
│   ├── contradictions/    # Flagged disagreements between sources
│   └── syntheses/         # Cross-source analyses, comparisons
└── scripts/               # Python utilities for scraping/extraction
```

## Naming Conventions

- **YouTube raw:** `{Sanitized_Title}_{YYYY-MM-DD}_{videoId}.md`
- **Articles raw:** `{Sanitized_Title}_{YYYY-MM-DD}_{domain}.md`
- **PDF/PPT raw:** `{Sanitized_Title}_{YYYY-MM-DD}.md`
- **Wiki pages:** Use clear, readable names. One canonical name per concept (no duplicates like `CAC.md` + `Customer Acquisition Cost.md` — pick one).
- **Filename sanitization:** Replace spaces with `_`, strip special chars, keep it filesystem-safe.

## Page Types (Brief)

Each wiki page has YAML frontmatter with `page_type`, `tags`, `source_count`, `last_updated`. Full templates are in PRD Section 4.

| Type | Location | Purpose |
|------|----------|---------|
| Source summary | `wiki/sources/` | 3-5 key takeaways per source, links to entities/concepts |
| Entity | `wiki/entities/` | Accumulative page per person/company/brand |
| Concept | `wiki/concepts/` | Accumulative page per idea/framework/metric |
| Topic | `wiki/topics/` | Broader themes (e.g., D2C India, Quick Commerce) |
| Channel | `wiki/channels/` | Hub page per YouTube channel |
| Contradiction | `wiki/contradictions/` | When sources disagree — stays unresolved until Nik reviews |
| Synthesis | `wiki/syntheses/` | Cross-source analysis, saved from queries |

## Core Principle: Accumulative Pages (CRITICAL)

When updating an existing entity or concept page:

1. **Read the existing page first** — understand what's already there
2. **Diff against new source** — identify what's genuinely new
3. **Only add what's additive:** new perspectives, concrete examples, data points, contradictions, nuances
4. **Attribute everything** — every claim links back to `[[Source: Episode Title]]`
5. **Never duplicate** — if the insight is already captured, skip it

A mature concept page should read like a well-edited Wikipedia article, not a log of summaries. See BRD Section 5b for the full accumulative model.

## Ingest Workflow

### Step 1: Scrape (Python)
Run the appropriate script to populate `/raw/`. Scripts handle extraction only.
```bash
python scripts/scrape_channel.py "<channel_url>" [--limit N]
python scripts/fetch_transcript.py "<video_url>"
```

### Step 2: Wiki Generation (Your Job)
For each file in `/raw/` with `status: raw` in frontmatter:

1. **Read the raw source IN FULL using chunked sequential reads.** Never generate wiki pages from partial reads. For files exceeding the token limit, read in sequential chunks (~200 lines or ~8000 chars at a time) covering the entire file. Take notes from each chunk, then write the wiki pages using the complete picture. Example: if a file has 500 lines, read lines 1-200, then 201-400, then 401-500.
2. Create source summary in `wiki/sources/`
3. Create or **update** entity pages in `wiki/entities/` (accumulative)
4. Create or **update** concept pages in `wiki/concepts/` (accumulative)
5. Check for contradictions → create page in `wiki/contradictions/` if found
6. Update channel page in `wiki/channels/` (if YouTube source)
7. Update `index.md` — add new pages, update source counts
8. Append to `log.md` — `## [YYYY-MM-DD] ingest | {Source Title} | {source_type}`
9. Set `status: wiki_processed` in the raw file's frontmatter

### Step 3: Batch Rules
- Process max **20 videos per session** for quality
- Git commit after each batch: `ingest: {source_type} | {description} | {count} sources`
- Next session picks up remaining `status: raw` files

## Query Workflow

When asked a question:
1. Read `index.md` to find relevant pages
2. Read those wiki pages
3. Synthesize answer with `[[page]]` citations
4. If answer is substantial, offer to save as `wiki/syntheses/` page

## Lint Checks (When Asked)

- Unresolved contradictions older than 2 weeks
- Orphan pages (no inbound links)
- Stale pages (not updated after newer relevant sources)
- Missing entity/concept pages for frequently mentioned items
- Near-duplicate pages that should be merged

## Rules

- **Never modify `/raw/`** except to update `status` in frontmatter
- **Use `[[wiki-links]]`** liberally for Obsidian graph connectivity
- **Oldest first** when ingesting a channel — wiki builds up naturally
- **Language priority:** English first, Hindi/Hinglish fallback
- **Keep concept pages under ~3000 words** — split into sub-pages if needed
