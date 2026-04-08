# PRD: Personal Knowledge Engine — Technical Specification

**Project Codename:** Vault  
**Author:** Nik + Claude  
**Date:** April 7, 2026  
**Status:** Draft  
**Companion doc:** [[BRD]] for vision, scope, and design decisions

---

## 1. System Overview

Vault is a local-first personal knowledge engine. It runs as a set of Python scripts operated by Claude Code, with Obsidian as the read/browse layer. There is no server, no database, no cloud dependency. The entire system is a Git repo of markdown files + a few Python utilities.

```
User → Claude Code → Python scripts → Markdown files → Obsidian (read)
         ↕                                    ↕
    Wiki generation                      Git versioning
```

---

## 2. Directory Structure

```
vault/
├── CLAUDE.md                  # Schema file — Claude Code's operating instructions
├── BRD.md                     # Business requirements (this stays for reference)
├── PRD.md                     # This file
├── index.md                   # Wiki content catalog (auto-maintained)
├── log.md                     # Chronological activity log (append-only)
│
├── raw/                       # Layer 1: Immutable raw sources
│   ├── youtube/               # YouTube transcripts
│   │   ├── Channel_Name_1/    # Subfolder per channel
│   │   │   ├── Video_Title_2024-03-15_dQw4w9WgXcQ.md
│   │   │   └── ...
│   │   └── Channel_Name_2/
│   ├── articles/              # Web articles converted to markdown
│   ├── pdfs/                  # PDF text extractions
│   └── ppts/                  # PPT text extractions
│
├── wiki/                      # Layer 2: LLM-generated knowledge wiki
│   ├── sources/               # One summary page per ingested source
│   ├── entities/              # People, companies, brands
│   ├── concepts/              # Recurring ideas, frameworks, metrics
│   ├── topics/                # Broader themes, industry verticals
│   ├── channels/              # Channel overview pages (YouTube)
│   ├── contradictions/        # Flagged disagreements between sources
│   └── syntheses/             # Cross-source analyses, comparisons
│
├── scripts/                   # Python utilities
│   ├── scrape_channel.py      # YouTube channel → video list + transcripts
│   ├── fetch_transcript.py    # Single video → transcript
│   ├── fetch_article.py       # URL → markdown article
│   ├── extract_pdf.py         # PDF → markdown
│   ├── extract_ppt.py         # PPT → markdown
│   └── utils.py               # Shared helpers (filename sanitization, etc.)
│
├── .gitignore
└── requirements.txt           # Python dependencies
```

---

## 3. Raw Source Format

Every raw source file is a markdown file with YAML frontmatter. This is the immutable source of truth.

### 3.1 YouTube Transcript

**Filename:** `{Sanitized_Video_Title}_{YYYY-MM-DD}_{videoId}.md`
- Date is video publish date
- videoId ensures uniqueness even if titles collide

```markdown
---
source_type: youtube_video
video_id: "dQw4w9WgXcQ"
title: "How boAt Built a ₹3000 Cr Brand"
channel: "Barbershop with Shantanu"
channel_id: "UCxxxxxx"
url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
publish_date: 2024-03-15
duration: "45:23"
language: "en"
is_auto_generated: true
ingested_date: 2026-04-07
status: raw  # raw | wiki_processed
---

# How boAt Built a ₹3000 Cr Brand

**Channel:** Barbershop with Shantanu  
**Date:** 2024-03-15  
**Duration:** 45:23  
**URL:** https://www.youtube.com/watch?v=dQw4w9WgXcQ

---

[Full transcript text here, clean paragraphs, no timestamps]
```

### 3.2 Web Article

**Filename:** `{Sanitized_Title}_{YYYY-MM-DD}_{domain}.md`

```markdown
---
source_type: article
title: "Why D2C Brands Are Returning to Marketplaces"
url: "https://example.com/article"
author: "Author Name"
domain: "example.com"
publish_date: 2024-06-01
ingested_date: 2026-04-07
status: raw
---

# Why D2C Brands Are Returning to Marketplaces

**Source:** example.com | **Author:** Author Name | **Date:** 2024-06-01

---

[Article text here]
```

### 3.3 PDF / PPT

**Filename:** `{Sanitized_Title}_{YYYY-MM-DD}.md`

```markdown
---
source_type: pdf  # or ppt
title: "Q3 2024 D2C Market Report"
original_filename: "D2C_Report_Q3.pdf"
author: "Redseer Strategy"
ingested_date: 2026-04-07
status: raw
---

# Q3 2024 D2C Market Report

**Source:** D2C_Report_Q3.pdf | **Author:** Redseer Strategy

---

[Extracted text here]
```

---

## 4. Wiki Page Templates

### 4.1 Source Summary (`/wiki/sources/`)

One per ingested source. Concise — for traceability, not for reading.

```markdown
---
page_type: source_summary
source_ref: "raw/youtube/Barbershop/How_boAt_Built_2024-03-15_dQw4w9WgXcQ.md"
source_type: youtube_video
channel: "Barbershop with Shantanu"
date: 2024-03-15
tags: [d2c, boat, consumer-electronics, branding]
last_updated: 2026-04-07
---

# Source: How boAt Built a ₹3000 Cr Brand

**Type:** YouTube Video | **Channel:** [[Channel - Barbershop with Shantanu]]  
**Date:** 2024-03-15 | **Raw:** [[How_boAt_Built_2024-03-15_dQw4w9WgXcQ]]

## Key Takeaways
- boAt started as a cable brand, pivoted to audio after seeing Beats' success in India
- Aman Gupta emphasizes "affordable lifestyle" positioning — not premium, not budget
- CAC was kept under ₹200 by heavy marketplace focus (Amazon, Flipkart did the distribution)
- Shifted to offline retail only after ₹500 Cr revenue — didn't go omnichannel too early

## Entities Mentioned
[[Aman Gupta]], [[boAt]], [[Amazon India]], [[Flipkart]]

## Concepts Touched
[[Unit Economics]], [[Marketplace vs Own Website]], [[Brand Positioning]], [[Omnichannel Strategy]]
```

### 4.2 Entity Page (`/wiki/entities/`)

Accumulative. Grows richer with each source.

```markdown
---
page_type: entity
entity_type: company  # person | company | brand | investor
name: "boAt"
tags: [d2c, consumer-electronics, audio, lifestyle]
source_count: 8
last_updated: 2026-04-07
---

# boAt

**Type:** D2C Consumer Electronics | **Founded:** 2016  
**Founders:** [[Aman Gupta]], [[Sameer Mehta]]

## Overview
[LLM-written synthesis of boAt's story, accumulated from multiple sources]

## Key Data Points
- CAC under ₹200 in early years (via marketplace-first strategy) — [[Source: How boAt Built...]]
- Revenue crossed ₹3000 Cr by FY24 — [[Source: ...]]
- [Each data point attributed to a source]

## Strategy & Approach
[Accumulated insights about boAt's strategy from multiple podcast appearances]

## Contradictions
- ⚠️ [[Contradiction: boAt Profitability Claims]] — conflicting numbers from 2023 vs 2024 interviews

## Sources
- [[Source: How boAt Built a ₹3000 Cr Brand]] (Barbershop, 2024-03-15)
- [[Source: Aman Gupta on Scaling Consumer Brands]] (Asymmetric, 2024-05-20)
- [...]
```

### 4.3 Concept Page (`/wiki/concepts/`)

Accumulative. The most important page type.

```markdown
---
page_type: concept
name: "Unit Economics"
aliases: [contribution margin, per-unit profitability]
tags: [finance, d2c-fundamentals, metrics]
source_count: 23
last_updated: 2026-04-07
---

# Unit Economics

## Definition
[Clean, synthesized definition — not from any single source but compiled from many]

## Key Frameworks
### Framework 1: [Name/Attribution]
[Description — attributed to source]

### Framework 2: [Name/Attribution]
[Description — attributed to source]

## How Indian D2C Brands Think About It
[Accumulated perspectives from multiple founders across multiple podcasts]

## Case Studies
### [[boAt]] — Marketplace-First Low CAC
[Specifics, numbers, attributed]

### [[Mamaearth]] — High CAC, Category Creation
[Specifics, numbers, attributed]

## Common Mistakes
[What founders say they got wrong — accumulated across sources]

## Evolution of Thinking
- **2020-2021:** Growth at all costs was accepted. Multiple founders cite "blitzscaling" mindset — [[Source: ...]]
- **2022-2023:** Post-funding winter, unit economics became table stakes — [[Source: ...]]
- **2024-2025:** Nuanced view — "depends on category and stage" — [[Source: ...]]

## Related Concepts
[[CAC]], [[LTV]], [[Contribution Margin]], [[Marketplace vs Own Website]], [[Blitzscaling]]

## Contradictions
- ⚠️ [[Contradiction: Acceptable CAC Range]] — founders cite wildly different numbers

## Sources
[List of all sources that contributed to this page]
```

### 4.4 Contradiction Page (`/wiki/contradictions/`)

```markdown
---
page_type: contradiction
status: unresolved  # unresolved | resolved | nuanced
tags: [unit-economics, cac]
created: 2026-04-07
last_updated: 2026-04-07
---

# Contradiction: Acceptable CAC Range for D2C

## The Disagreement

**Claim A:** CAC should be under ₹200 for sustainable D2C  
**Source:** [[Aman Gupta]] on [[Source: How boAt Built...]] (2024-03-15)  
**Context:** Consumer electronics, marketplace-first model

**Claim B:** CAC of ₹800-1200 is acceptable if LTV justifies it  
**Source:** [[Varun Alagh]] on [[Source: Mamaearth's Journey...]] (2024-06-10)  
**Context:** Personal care, category creation, repeat purchase model

## Why They Might Both Be Right
[LLM's initial analysis — may be category-dependent, stage-dependent, etc.]

## Affected Pages
- [[Unit Economics]] — flagged in "Contradictions" section
- [[CAC]] — flagged
- [[boAt]] — references Claim A
- [[Mamaearth]] — references Claim B

## Resolution
*Unresolved — pending discussion with Nik*
```

### 4.5 Channel Page (`/wiki/channels/`)

```markdown
---
page_type: channel
channel_name: "Barbershop with Shantanu"
channel_id: "UCxxxxxx"
channel_url: "https://www.youtube.com/@barbershop"
total_videos_ingested: 45
tags: [d2c, startups, founders, india]
last_updated: 2026-04-07
---

# Channel: Barbershop with Shantanu

**Host:** [[Shantanu Deshpande]]  
**Focus:** D2C founders, brand building, Indian startup ecosystem  
**Videos Ingested:** 45 / 120 total

## Signature Topics
[[Brand Positioning]], [[Marketplace vs Own Website]], [[Fundraising]], [[Unit Economics]]

## Notable Guests
[[Aman Gupta]], [[Varun Alagh]], [[Ghazal Alagh]], [[Vineeta Singh]]

## Ingested Episodes
| Date | Title | Source Page |
|------|-------|------------|
| 2024-03-15 | How boAt Built a ₹3000 Cr Brand | [[Source: How boAt Built...]] |
| ... | ... | ... |
```

---

## 5. Scripts Specification

### 5.1 `scrape_channel.py`

**Purpose:** Given a YouTube channel URL/handle/ID, fetch all video metadata and transcripts.

**Dependencies:** `scrapetube`, `youtube-transcript-api`

**Input:** Channel URL, optional limit, optional language priority

**Output:** Markdown files in `/raw/youtube/{Channel_Name}/`

**Behavior:**
- Uses `scrapetube.get_channel(content_type="videos")` — no Shorts, no Streams
- Sorts by oldest first (per BRD decision)
- For each video:
  - Fetches transcript via `youtube-transcript-api` (language priority: `["en", "hi", "en-IN"]`)
  - Cleans transcript: removes excessive newlines, joins short fragments into paragraphs
  - Writes markdown file with YAML frontmatter
  - Sets `status: raw` in frontmatter
- **Resume support:** Checks existing files in the channel subfolder by videoId. Skips already-scraped videos.
- **Progress:** Prints `[X/Y] Title (videoId)` for each video
- **Error handling:** Logs failed transcripts (no captions, age-restricted, etc.) to a `_scrape_errors.json` file in the channel subfolder. Continues with remaining videos.
- **Rate limiting:** 1-second delay between transcript fetches (configurable)

**CLI:**
```bash
python scripts/scrape_channel.py "https://www.youtube.com/@channel" [--limit 50] [--lang en hi] [--delay 1.0]
```

### 5.2 `fetch_transcript.py`

**Purpose:** Fetch transcript for a single YouTube video.

**Input:** Video URL or ID

**Output:** Single markdown file in `/raw/youtube/_singles/`

**CLI:**
```bash
python scripts/fetch_transcript.py "https://www.youtube.com/watch?v=videoId"
```

### 5.3 `fetch_article.py`

**Purpose:** Fetch and convert a web article to clean markdown.

**Dependencies:** `requests`, `readability-lxml`, `markdownify` (or similar)

**Input:** Article URL

**Output:** Markdown file in `/raw/articles/`

**Behavior:**
- Fetches page HTML
- Extracts main article content (strips nav, ads, sidebar)
- Converts to clean markdown
- Extracts metadata: title, author, publish date, domain
- Writes with YAML frontmatter

**CLI:**
```bash
python scripts/fetch_article.py "https://example.com/article"
```

### 5.4 `extract_pdf.py`

**Purpose:** Extract text from a PDF file.

**Dependencies:** `PyPDF2` or `pdfplumber`

**Input:** Path to PDF file

**Output:** Markdown file in `/raw/pdfs/`

**CLI:**
```bash
python scripts/extract_pdf.py /path/to/document.pdf
```

### 5.5 `extract_ppt.py`

**Purpose:** Extract text and structure from a PowerPoint file.

**Dependencies:** `python-pptx`

**Input:** Path to .pptx file

**Output:** Markdown file in `/raw/ppts/`

**Behavior:**
- Extracts text from each slide
- Preserves slide structure (slide number, title, content)
- Extracts speaker notes if present

**CLI:**
```bash
python scripts/extract_ppt.py /path/to/presentation.pptx
```

### 5.6 `utils.py`

**Shared utilities:**
- `sanitize_filename(title: str) -> str` — make strings safe for filenames
- `extract_video_id(url: str) -> str` — parse YouTube URLs
- `extract_channel_identifier(url: str) -> dict` — parse channel URLs into scrapetube kwargs
- `get_existing_video_ids(channel_dir: Path) -> set` — for resume support
- `update_frontmatter(filepath: Path, key: str, value: any)` — update YAML frontmatter fields

---

## 6. Wiki Generation (Claude Code's Job)

The Python scripts handle extraction (Layer 1). Wiki generation (Layer 2) is done by Claude Code itself, guided by CLAUDE.md.

### 6.1 Ingest Workflow (What Claude Code Does)

When asked to ingest a source or batch of sources:

**Step 1: Check raw sources**
- Read `/raw/` to find files with `status: raw` in frontmatter
- These are unprocessed sources waiting for wiki integration

**Step 2: For each unprocessed source, read it and:**

a. **Create source summary** in `/wiki/sources/`
   - Extract 3-5 key takeaways
   - Identify entities mentioned (people, companies, brands)
   - Identify concepts/topics discussed
   - Tag appropriately

b. **Update entity pages** in `/wiki/entities/`
   - For each entity mentioned: check if page exists
   - If exists: read it, add only new information (accumulative model)
   - If new: create page from template
   - Always attribute claims to source

c. **Update concept pages** in `/wiki/concepts/`
   - Same accumulative logic as entities
   - Add new perspectives, examples, data points — not redundant content
   - Update "Evolution of Thinking" section if source is from a different time period

d. **Check for contradictions**
   - Compare claims in new source against existing wiki pages
   - If contradiction found: create contradiction page in `/wiki/contradictions/`
   - Add inline flag (⚠️) on affected entity/concept pages with link to contradiction page

e. **Update channel page** if source is YouTube
   - Add episode to the channel's ingested list
   - Update signature topics if new topic emerged

f. **Update `index.md`**
   - Add new pages to appropriate category
   - Update source counts on existing entries

g. **Append to `log.md`**
   - `## [YYYY-MM-DD] ingest | {Source Title} | {source_type}`

**Step 3: Mark source as processed**
- Update frontmatter: `status: wiki_processed`

### 6.2 Batch Processing

For bulk channel ingestion (20 videos per batch):
1. Claude Code runs `scrape_channel.py` first (all videos, pure Python)
2. Then processes 20 raw transcripts through the wiki generation workflow
3. After each batch: commits to Git, reports summary
4. Next session: picks up remaining `status: raw` files

### 6.3 Query Workflow

When asked a question:
1. Read `index.md` to find relevant wiki pages
2. Read those pages
3. Synthesize answer with `[[page]]` citations
4. If answer is substantial, offer to save as synthesis page in `/wiki/syntheses/`

---

## 7. CLAUDE.md Schema (Summary)

The full `CLAUDE.md` will be generated when we start building. It will contain:

- Project overview (one paragraph)
- Directory structure reference
- Page templates for each wiki page type
- Ingest workflow (step-by-step, referencing this PRD)
- Query workflow
- Lint workflow
- Accumulative page rules (from BRD Section 5b)
- Naming conventions
- Frontmatter schema for each source and page type
- Git commit conventions
- What to do when things go wrong (missing transcripts, malformed sources, etc.)

---

## 8. Dependencies

### Python (requirements.txt)
```
scrapetube>=2.5.0
youtube-transcript-api>=1.2.0
requests>=2.31.0
readability-lxml>=0.8.1
markdownify>=0.11.0
PyPDF2>=3.0.0
python-pptx>=0.6.21
pyyaml>=6.0
```

### External Tools
- **Obsidian** — installed on user's machine, pointed at vault folder
- **Git** — for version history
- **Claude Code** — for wiki generation and querying

### No API Keys Required
- `scrapetube` scrapes YouTube without API key
- `youtube-transcript-api` fetches transcripts without API key
- All processing is local

---

## 9. Git Workflow

- Every ingest batch = one commit
- Commit message format: `ingest: {source_type} | {description} | {count} sources`
  - Example: `ingest: youtube_channel | Barbershop_with_Shantanu | 20 videos`
  - Example: `ingest: article | Why D2C Brands Return to Marketplaces`
- Wiki updates from queries: `query: {question summary}`
- Lint fixes: `lint: {description}`
- `.gitignore`: Python cache, virtual env, OS files

---

## 10. Testing Plan

### Phase 1: Scraper Testing
- Pick a small channel (10-15 videos)
- Run `scrape_channel.py`
- Verify: all videos scraped, no Shorts included, frontmatter correct, filenames clean, resume works

### Phase 2: Wiki Generation Testing
- Take 5 scraped transcripts
- Run through wiki generation workflow manually via Claude Code
- Verify: source summaries created, entity pages created, concept pages created, index updated, log updated
- Check quality: are the summaries good? Are the right entities extracted? Are concept pages well-structured?

### Phase 3: Accumulative Testing
- Ingest 5 more videos from the same channel
- Verify: existing concept pages are updated (not duplicated), new information is additive, contradictions are caught
- This is the critical test — does the accumulative model actually work?

### Phase 4: Cross-Source Testing
- Ingest a video from a different channel covering similar topics
- Verify: concept pages integrate perspectives from both channels, entity pages are shared, contradictions across channels are flagged

---

## 11. Known Limitations & Future Considerations

1. **Transcript quality:** Auto-generated YouTube captions have errors (especially Hindi/Hinglish). The wiki may inherit these. Mitigation: note `is_auto_generated: true` in frontmatter, treat auto-generated transcripts as lower confidence.

2. **Context window:** For large concept pages (after many ingestions), Claude Code may struggle to read the full page + new transcript in one context window. Mitigation: keep concept pages focused; split into sub-pages if they exceed ~3000 words.

3. **Token cost:** Each wiki generation pass requires Claude Code to read existing pages + new source + write updates. For 200 videos, this is significant. Mitigation: batch at 20, review quality, adjust.

4. **Stale wiki:** If you scrape 200 transcripts but only wiki-process 40, you have 160 raw sources sitting unprocessed. The system should make it easy to see this gap (`status: raw` count vs `status: wiki_processed` count).

5. **No real-time sync:** Obsidian watches the filesystem, so changes appear quickly. But there's no notification system — you have to open Obsidian and look.

6. **Search at scale:** `index.md` works for ~200 pages. Beyond that, we'll need `qmd` or a custom search script. This is a V2 concern.
