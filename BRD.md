# BRD: Personal Knowledge Engine (Project Codename: "Vault")

**Author:** Nik + Claude  
**Date:** April 7, 2026  
**Status:** Draft — open for discussion

---

## 1. Vision

A personal knowledge system where an LLM (via Claude Code) continuously ingests raw sources — YouTube transcripts, web articles, PDFs, PPTs, VC notes — and compiles them into a living, interlinked Obsidian wiki. Knowledge is built up incrementally, not re-derived on every question.

**The human curates. The LLM builds.**

You point it at sources. It reads, summarizes, cross-references, flags contradictions, and maintains the wiki. Over time, the wiki becomes a compounding asset — richer with every source added and every question asked.

---

## 2. Problem Statement

Today, consuming knowledge from YouTube channels, articles, PDFs, and notes results in scattered, non-compounding information. You watch 50 videos from a D2C podcast series, and two weeks later you remember fragments. There's no structured artifact that captures what you learned, connects the dots, or tells you when two sources disagree.

RAG-style tools (NotebookLM, ChatGPT uploads) retrieve chunks at query time but build nothing persistent. The synthesis is redone from scratch every time.

---

## 3. Target User

Nik (solo user). Professional context: CEO's Office at Lenskart. Primary knowledge domains starting with D2C and Indian retail, expanding to broader retail, strategy, and personal interests.

---

## 4. Source Types (Day 1)

| Source Type | Input Method | Processing |
|---|---|---|
| **YouTube Channel** | Drop channel URL → bulk-ingest all videos (not Shorts) | Scrape video list → fetch transcripts → save as markdown → auto-generate wiki pages |
| **YouTube Video** | Drop individual video URL | Fetch transcript → save as markdown → auto-generate wiki pages |
| **Web Article** | Drop URL | Fetch content → convert to markdown → auto-generate wiki pages |
| **PDF** | Drop file | Extract text → save raw → auto-generate wiki pages |
| **PPT** | Drop file | Extract text + structure → save raw → auto-generate wiki pages |

**Language priority:** English first, Hindi fallback (for Indian D2C content that may have Hindi/Hinglish captions).

---

## 5. Architecture (Three Layers)

### Layer 1: Raw Sources (`/raw/`)
- Immutable. LLM reads but never modifies.
- Source of truth. Every wiki claim traces back here.
- Organized by type: `/raw/youtube/`, `/raw/articles/`, `/raw/pdfs/`, `/raw/ppts/`
- YouTube transcripts stored as markdown files: `{Video_Title}_{YYYY-MM-DD}_{videoId}.md`
- Each raw file has YAML frontmatter: source URL, date, channel/author, type, ingestion date

### Layer 2: The Wiki (`/wiki/`)
- LLM-generated markdown files. LLM owns this entirely.
- Page types:
  - **Source summaries** — one page per ingested source (key takeaways, 3-5 bullet synthesis)
  - **Entity pages** — people, companies, brands (e.g., `Peyush Bansal.md`, `boAt.md`, `Mamaearth.md`)
  - **Concept pages** — recurring ideas/frameworks (e.g., `Unit Economics.md`, `CAC Payback.md`, `Omnichannel.md`)
  - **Topic pages** — broader themes (e.g., `D2C India Landscape.md`, `Quick Commerce.md`)
  - **Contradiction pages** — when sources disagree, a dedicated page captures both claims with links, left unresolved until discussed (`/wiki/contradictions/`)
  - **Synthesis pages** — cross-source analyses, comparisons, timelines
- All pages use `[[wiki-links]]` for Obsidian graph view
- YAML frontmatter on every page: tags, source count, last updated, page type

### Layer 3: The Schema (`CLAUDE.md`)
- Lives in project root. Instructions for Claude Code on how to operate.
- Defines: directory structure, naming conventions, page templates, ingestion workflow, query workflow, lint workflow
- Co-evolved by Nik and Claude Code over time as patterns emerge

---

## 5b. Accumulative Page Intelligence (Critical Design Principle)

This is the heart of what makes the wiki useful vs. just a transcript dump.

### The Problem with Naive Ingestion
If you ingest 100 episodes of Barbershop / Asymmetric, many episodes cover overlapping topics — D2C unit economics, fundraising, brand building, marketplace vs website, etc. The guests and examples differ, but the concepts recur. A naive system would either:
- Create 100 separate pages that repeat the same ideas, or
- Blindly append to a concept page until it becomes an unreadable wall of text

Both are useless.

### The Accumulative Model
When a concept page already exists (e.g., `[[Unit Economics]]`), the LLM must:

1. **Read the existing page first** — understand what's already captured
2. **Diff the new source against existing knowledge** — what's genuinely new?
3. **Only add what's additive:**
   - A new perspective or framework not already captured
   - A concrete example/case study that illustrates an existing point better
   - A data point or number (e.g., "Aman Gupta says boAt's CAC was ₹180 in 2021")
   - A contradiction or evolution (e.g., "In 2023, Shantanu said X. In 2025, he revised this to Y")
   - A nuance that refines the existing understanding
4. **Attribute everything** — every claim links back to `[[Source: Episode Title]]` so you can trace it

### What a Good Concept Page Looks Like

A mature `[[Unit Economics]]` page after 30 ingestions should read like a **well-edited Wikipedia article**, not a log of 30 summaries. It should have:
- A clean definition/overview at the top
- Key frameworks and mental models (attributed)
- Concrete examples and case studies (with source links)
- Common mistakes/misconceptions mentioned by guests
- A "Sources" section at the bottom listing every video that contributed
- A "Contradictions" section if relevant, linking to `/wiki/contradictions/`

### Clustering Related Topics
Some topics are closely related but distinct — e.g., "CAC" vs "Unit Economics" vs "Contribution Margin." The LLM should:
- Create separate pages for genuinely distinct concepts
- Use `[[wiki-links]]` liberally between related pages
- Avoid creating near-duplicate pages (e.g., don't have both `CAC.md` and `Customer Acquisition Cost.md` — pick one, alias the other)
- When in doubt, merge into the broader concept page and use subheadings

### Channel-Level Intelligence
When multiple episodes come from the same channel (Barbershop, Asymmetric, Tokers House), the LLM should recognize the channel's "signature" topics and recurring guests. A channel page (e.g., `[[Channel - Barbershop with Shantanu]]`) acts as a hub — linking to all ingested episodes and the key entities/concepts that channel covers most. This helps avoid redundancy: if Shantanu's view on "marketplace vs D2C website" is well-captured from Episode 12, Episode 47 covering the same ground with minor updates should only add the delta.

---

## 5c. Query & Chat Model (How You Talk to the Wiki)

### What "Chatting with the Wiki" Means
When you open Claude Code in the Vault folder and ask a question, Claude Code:
1. Reads `CLAUDE.md` (knows it's operating on a wiki)
2. Reads `index.md` (knows what pages exist)
3. Searches for relevant wiki pages based on your question
4. Reads those pages (which are pre-compiled, cross-referenced knowledge)
5. Synthesizes an answer with `[[page links]]` as citations

This is **not RAG over raw transcripts**. Claude is reading organized, de-duplicated, cross-referenced knowledge. The quality of answers is dramatically better because the hard work (synthesis, contradiction detection, cross-referencing) was done at ingest time, not at query time.

### How This Differs from Vanilla Claude
- Vanilla Claude: knows general knowledge, doesn't know what Aman Gupta said about boAt's CAC on Barbershop Episode 34
- Wiki-enhanced Claude: has a compiled page on `[[boAt]]` with sourced claims from 8 different podcast appearances, cross-linked to `[[Unit Economics]]` and `[[Aman Gupta]]`

### Compounding Through Queries
When you ask a good question and Claude gives a good answer, that answer can be saved back as a new wiki page (a Synthesis page). For example:
- You ask: "Compare how boAt and Mamaearth approached marketplace dependency"
- Claude synthesizes from 12 source pages
- You say: "Save this as a wiki page"
- Now `[[Comparison - boAt vs Mamaearth Marketplace Strategy]]` exists in the wiki, linked from both entity pages
- Future queries can draw on this synthesis — knowledge compounds

### What Claude Does NOT Become
Claude is not "trained" on your wiki permanently. Each conversation is a fresh session where Claude reads the wiki files. But because the wiki is well-structured, it effectively functions as if Claude has deep domain expertise. The wiki is the memory; Claude is the intelligence that operates on it.

---

## 6. Key Operations

### 6.1 Ingest: YouTube Channel (Bulk)
This is the primary Day 1 workflow.

**Trigger:** User provides a YouTube channel URL.

**Flow:**
1. Scrape all video IDs from channel (videos only, no Shorts, no Streams)
2. For each video:
   a. Fetch transcript (English preferred, Hindi fallback)
   b. Save raw transcript as markdown in `/raw/youtube/` with frontmatter (title, date, channel, URL, video ID)
   c. Generate/update wiki pages:
      - Source summary page in `/wiki/sources/`
      - Update relevant entity pages (people/companies mentioned)
      - Update relevant concept/topic pages
      - Flag contradictions with existing wiki content → create contradiction page
      - Update `index.md`
      - Append to `log.md`
3. Generate channel overview page (if new channel)

**Scale consideration:** A channel with 200+ videos will take time. The system should:
- Support resuming (skip already-ingested videos based on video ID)
- Show progress (X of Y videos processed)
- Handle failures gracefully (log failed transcripts, continue with rest)
- Rate-limit API calls to avoid blocking

### 6.2 Ingest: Single Source
**Trigger:** User drops a link (YouTube video, article) or file (PDF, PPT).

**Flow:**
1. Detect source type from URL/file extension
2. Extract content → save raw
3. Discuss with user (optional — for high-value sources, Claude Code reads it and surfaces key takeaways before filing)
4. Generate/update wiki pages (same as channel flow step 2c)

### 6.3 Query
**Trigger:** User asks a question against the wiki.

**Flow:**
1. Claude Code reads `index.md` to identify relevant pages
2. Reads relevant wiki pages
3. Synthesizes answer with citations (`[[Source Page]]` links)
4. If answer is valuable, offer to file it as a new wiki page (synthesis/analysis)

### 6.4 Lint
**Trigger:** User asks for a health check, or periodically.

**Checks:**
- Contradictions unresolved for >2 weeks
- Orphan pages (no inbound links)
- Stale pages (not updated after newer relevant sources)
- Important entities/concepts mentioned but lacking their own page
- Missing cross-references
- Data gaps that could be filled with a web search or new source

---

## 7. Indexing & Navigation

### `index.md`
- Content-oriented catalog of all wiki pages
- Organized by category: Entities, Concepts, Topics, Sources, Contradictions, Syntheses
- Each entry: `[[Page Name]]` — one-line summary — source count — last updated
- Updated on every ingest
- Claude Code reads this first when answering queries

### `log.md`
- Chronological, append-only
- Format: `## [YYYY-MM-DD] action | Detail`
  - Actions: `ingest`, `query`, `lint`, `resolve`, `update`
- Parseable: `grep "^## \[" log.md | tail -10`

---

## 8. Tech Stack

| Component | Tool | Why |
|---|---|---|
| Wiki reader/browser | Obsidian | Graph view, [[wiki-links]], Dataview, local-first, just markdown files |
| Wiki builder/editor | Claude Code | Operates directly on the folder, reads/writes markdown |
| YouTube scraper | `scrapetube` (Python) | No API key needed, filters Shorts via `content_type="videos"` |
| Transcript fetcher | `youtube-transcript-api` (Python) | No API key, supports auto-generated captions |
| Article fetcher | `requests` + `readability-lxml` or similar | Extract clean article text from URLs |
| PDF/PPT reader | Python (`PyPDF2`, `python-pptx`) | Extract text from uploaded files |
| Search (future) | `qmd` or custom BM25 | When index.md doesn't scale anymore (~200+ pages) |
| Version control | Git | Every ingest = commit. Full history. |

---

## 9. Scope: V1 vs Later

### V1 (Build Now)
- [ ] YouTube channel bulk ingestion (scrape → transcripts → raw markdown)
- [ ] YouTube single video ingestion
- [ ] Wiki auto-generation on ingest (source summaries, entity pages, concept pages)
- [ ] Contradiction detection and filing
- [ ] `index.md` and `log.md` maintenance
- [ ] `CLAUDE.md` schema for Claude Code
- [ ] Resume support (don't re-ingest already-processed videos)
- [ ] Basic query workflow (read index → find pages → synthesize)

### V2 (Later)
- [ ] Web article ingestion (URL → markdown → wiki)
- [ ] PDF / PPT ingestion
- [ ] Lint workflow
- [ ] Proper search (BM25/vector) when wiki outgrows index
- [ ] Obsidian Dataview queries via YAML frontmatter
- [ ] Batch channel comparison (e.g., what do 3 D2C podcasts agree/disagree on?)

### V3 (Maybe)
- [ ] Scheduled ingestion (cron: check channels for new videos weekly)
- [ ] MCP server so Claude Desktop can also operate on the wiki
- [ ] Export: generate slide decks, reports, briefing docs from wiki pages
- [ ] Multi-user / shared wiki

---

## 10. Open Questions

1. **Wiki page granularity:** ✅ **Resolved.** One concise source summary per video (key takeaways + link to raw). Real value lives in accumulative concept/entity pages. Source summaries are for traceability, not for reading.

2. **Contradiction resolution flow:** ✅ **Resolved.** Dedicated contradiction pages in `/wiki/contradictions/` AND inline flags on affected concept/entity pages. Contradictions stay unresolved until Nik reviews and discusses with Claude Code.

3. **How much wiki to generate per video?** ✅ **Resolved.** Full-depth auto-generation on ingest, using the accumulative model (Section 5b). LLM only adds what's genuinely new to each concept page.

4. **Naming convention & folder structure:** ✅ **Resolved.** Subfolders per channel: `/raw/youtube/Barbershop_with_Shantanu/{Video_Title}_{YYYY-MM-DD}_{videoId}.md`

5. **Starting channels:** ⏳ **Pending Nik's input.** Need 2-3 concrete YouTube channels to test V1.

6. **Ingest ordering:** ✅ **Resolved.** Oldest first — wiki builds up naturally, contradictions show evolution over time.

7. **Batch size for wiki generation:** ✅ **Resolved.** Transcript scraping runs for all videos at once (pure Python, no LLM cost). Wiki generation batched at 20 videos per session for quality review. Resume support ensures next batch picks up where the last left off.

---

## 11. Success Criteria

The system works if:
- You can point it at a YouTube channel and walk away while it ingests
- Coming back, you find a navigable wiki in Obsidian with entity pages, concept pages, and cross-references you didn't have to write
- You can ask Claude Code "What does the wiki say about X?" and get a sourced answer
- When two videos contradict each other, you can see it without having to watch both
- The wiki gets richer over time, not messier
