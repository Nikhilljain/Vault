"""Shared utilities for Vault scraper scripts."""

from __future__ import annotations

import re
import json
from datetime import datetime, timedelta
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Filename helpers
# ---------------------------------------------------------------------------

def sanitize_filename(title: str) -> str:
    """Replace spaces with _ and strip non-filesystem-safe characters."""
    name = title.strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)  # strip illegal chars
    name = re.sub(r'\s+', '_', name)                      # spaces → underscores
    name = re.sub(r'_+', '_', name)                        # collapse runs
    name = name.strip('_.')                                # trim edges
    return name[:200]                                      # cap length


# ---------------------------------------------------------------------------
# YouTube URL parsing
# ---------------------------------------------------------------------------

_YT_VIDEO_PATTERNS = [
    re.compile(r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([A-Za-z0-9_-]{11})'),
]

def extract_video_id(url: str) -> str:
    """Extract the 11-char video ID from a YouTube URL."""
    for pat in _YT_VIDEO_PATTERNS:
        m = pat.search(url)
        if m:
            return m.group(1)
    # Maybe it's already a bare ID
    if re.fullmatch(r'[A-Za-z0-9_-]{11}', url):
        return url
    raise ValueError(f"Cannot extract video ID from: {url}")


def extract_channel_identifier(url: str) -> dict:
    """Parse a YouTube channel URL into kwargs for scrapetube.get_channel().

    Supports:
      - https://www.youtube.com/@handle
      - https://www.youtube.com/c/CustomName
      - https://www.youtube.com/channel/UCxxxxxx
      - https://www.youtube.com/user/username
    """
    url = url.strip().rstrip('/')

    # @handle or /c/ → pass as channel_url (scrapetube handles these)
    if '/@' in url or '/c/' in url:
        return {'channel_url': url}

    # /channel/UCxxxxxx → channel_id
    m = re.search(r'/channel/(UC[A-Za-z0-9_-]+)', url)
    if m:
        return {'channel_id': m.group(1)}

    # /user/username → channel_url
    if '/user/' in url:
        return {'channel_url': url}

    # Fallback: treat the whole thing as a channel_url
    return {'channel_url': url}


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

_RELATIVE_DATE_RE = re.compile(
    r'(\d+)\s+(second|minute|hour|day|week|month|year)s?\s+ago',
    re.IGNORECASE,
)

_UNIT_TO_DAYS = {
    'second': 0,
    'minute': 0,
    'hour': 0,
    'day': 1,
    'week': 7,
    'month': 30,
    'year': 365,
}

def parse_relative_date(text: str) -> str:
    """Convert 'X units ago' to an approximate YYYY-MM-DD string.

    Falls back to today's date if parsing fails.
    """
    m = _RELATIVE_DATE_RE.search(text)
    if not m:
        return datetime.now().strftime('%Y-%m-%d')
    quantity = int(m.group(1))
    unit = m.group(2).lower()
    days = _UNIT_TO_DAYS.get(unit, 0) * quantity
    approx = datetime.now() - timedelta(days=days)
    return approx.strftime('%Y-%m-%d')


# ---------------------------------------------------------------------------
# Resume support
# ---------------------------------------------------------------------------

def get_existing_video_ids(channel_dir: Path) -> set:
    """Scan a channel directory for already-scraped video IDs.

    Expects filenames like: {Title}_{YYYY-MM-DD}_{videoId}.md
    """
    ids = set()
    if not channel_dir.is_dir():
        return ids
    for f in channel_dir.glob('*.md'):
        # videoId is the 11-char segment right before .md
        stem = f.stem  # filename without .md
        parts = stem.rsplit('_', 1)
        if len(parts) == 2 and re.fullmatch(r'[A-Za-z0-9_-]{11}', parts[1]):
            ids.add(parts[1])
    return ids


# ---------------------------------------------------------------------------
# Transcript cleaning
# ---------------------------------------------------------------------------

def clean_transcript(segments: list[dict]) -> str:
    """Join transcript segments into clean paragraph text.

    Merges short fragments, removes excessive whitespace.
    """
    if not segments:
        return ''

    lines = []
    current = []
    char_count = 0

    for seg in segments:
        text = seg.get('text', '').strip()
        if not text:
            continue
        current.append(text)
        char_count += len(text)

        # Break into paragraphs roughly every ~500 chars or at sentence ends
        if char_count >= 500 and text[-1] in '.!?':
            lines.append(' '.join(current))
            current = []
            char_count = 0

    if current:
        lines.append(' '.join(current))

    return '\n\n'.join(lines)


# ---------------------------------------------------------------------------
# Markdown writing
# ---------------------------------------------------------------------------

def write_raw_markdown(path: Path, frontmatter: dict, header: str, body: str):
    """Write a markdown file with YAML frontmatter."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True, sort_keys=False)
    content = f"---\n{fm}---\n\n{header}\n\n---\n\n{body}\n"
    path.write_text(content, encoding='utf-8')


# ---------------------------------------------------------------------------
# Error logging
# ---------------------------------------------------------------------------

def log_scrape_error(error_file: Path, video_id: str, title: str, error: str):
    """Append a scrape error to the channel's _scrape_errors.json."""
    errors = []
    if error_file.exists():
        try:
            errors = json.loads(error_file.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            errors = []
    errors.append({'video_id': video_id, 'title': title, 'error': error})
    error_file.write_text(json.dumps(errors, indent=2, ensure_ascii=False), encoding='utf-8')
