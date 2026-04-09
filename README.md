# Vault

A personal knowledge engine that ingests raw sources (YouTube transcripts, articles, PDFs) and builds a living, interlinked Obsidian wiki using Claude Code as the AI backbone.

## How It Works

1. **Scrape** raw sources into `/raw/` using Python scripts
2. **Generate wiki** pages using Claude Code — source summaries, entity profiles, concept pages, cross-references
3. **Query** the wiki through Claude Code, which reads the index and synthesizes answers with citations

The wiki follows an **accumulative model** — entity and concept pages grow richer with each new source, like a personal Wikipedia.

## Directory Structure

```
raw/               # Immutable raw sources (transcripts, articles, PDFs)
wiki/
  sources/         # One summary per ingested source
  entities/        # People, companies, brands
  concepts/        # Recurring ideas, frameworks, metrics
  topics/          # Broader themes
  channels/        # YouTube channel overview pages
  contradictions/  # Flagged disagreements between sources
  syntheses/       # Cross-source analyses
scripts/           # Python scraping utilities
index.md           # Wiki content catalog
log.md             # Chronological activity log
CLAUDE.md          # Claude Code operating instructions
BRD.md / PRD.md    # Full specs
```

## Setup

### Prerequisites

- Python 3.10+
- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- [Obsidian](https://obsidian.md/) (optional, for browsing the wiki)

### Install dependencies

```bash
pip install youtube-transcript-api scrapetube requests beautifulsoup4
```

### Scrape a YouTube channel

```bash
python scripts/scrape_channel.py "https://www.youtube.com/@ChannelHandle" --limit 10
```

Options:
- `--limit N` — max videos to fetch (default: all)
- `--lang en hi` — language priority for transcripts
- `--delay 3.0` — seconds between fetches
- `--min-duration 30` — minimum video length in minutes (default: 30)
- `--cookies path/to/cookies.txt` — Netscape-format cookies file to bypass YouTube IP blocks

### Generate wiki pages

Open the project in Claude Code and ask it to ingest the scraped sources:

```
ingest the raw files for [Channel Name]
```

Claude Code reads each raw transcript, creates source summaries, updates entity/concept pages, and maintains the index — all following the rules in `CLAUDE.md`.

### Query the wiki

Ask Claude Code any question and it will search the wiki, read relevant pages, and synthesize an answer with `[[wiki-link]]` citations.

## Viewing in Obsidian

Open this folder as an Obsidian vault. The wiki uses `[[wikilinks]]` throughout, so the graph view shows how entities, concepts, and sources interconnect.

## Currently Ingested

- **ASYMMETRIC Podcast** — 10 episodes on Indian startups, venture capital, consumer trends
- **Lightbox** — 2 episodes (gaming, crypto)

See `index.md` for the full catalog.
