#!/usr/bin/env python3
"""Scrape all video transcripts from a YouTube channel into raw/ markdown files."""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime
from pathlib import Path

import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)

from utils import (
    clean_transcript,
    extract_channel_identifier,
    fetch_video_metadata,
    get_existing_video_ids,
    log_scrape_error,
    parse_duration_seconds,
    parse_relative_date,
    sanitize_filename,
    write_raw_markdown,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_YT_DIR = PROJECT_ROOT / 'raw' / 'youtube'


def get_video_title(video: dict) -> str:
    try:
        return video['title']['runs'][0]['text']
    except (KeyError, IndexError):
        return video.get('videoId', 'Untitled')


def get_video_duration(video: dict) -> str:
    try:
        return video['lengthText']['simpleText']
    except (KeyError, TypeError):
        return 'unknown'


def get_publish_date_text(video: dict) -> str:
    try:
        return video['publishedTimeText']['simpleText']
    except (KeyError, TypeError):
        return ''


def channel_name_from_url(url: str) -> str:
    """Extract a human-readable channel name from the URL.

    @handle → handle, /c/Name → Name, /channel/UCxxx → UCxxx, /user/name → name
    """
    import re as _re
    url = url.strip().rstrip('/')
    # @handle
    m = _re.search(r'/@([^/]+)', url)
    if m:
        return m.group(1)
    # /c/CustomName
    m = _re.search(r'/c/([^/]+)', url)
    if m:
        return m.group(1)
    # /channel/UCxxxxxx
    m = _re.search(r'/channel/([^/]+)', url)
    if m:
        return m.group(1)
    # /user/username
    m = _re.search(r'/user/([^/]+)', url)
    if m:
        return m.group(1)
    return 'Unknown_Channel'


def get_channel_name_from_video(video: dict) -> str:
    try:
        return video['ownerText']['runs'][0]['text']
    except (KeyError, IndexError):
        try:
            return video['shortBylineText']['runs'][0]['text']
        except (KeyError, IndexError):
            return ''


def get_channel_id_from_video(video: dict) -> str:
    try:
        return video['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId']
    except (KeyError, IndexError):
        return ''


def fetch_transcript_for_video(ytt_api, video_id: str, languages: list[str]):
    """Fetch transcript and detect if auto-generated.

    Returns (segments, language_code, is_auto_generated).
    """
    # First, list available transcripts to detect auto-generation
    transcript_list = ytt_api.list(video_id)
    is_auto = False
    lang_code = ''

    for t in transcript_list:
        if t.language_code in languages:
            is_auto = t.is_generated
            lang_code = t.language_code
            break
    else:
        # Check if any transcript matches at all (fetch will pick the best)
        for t in transcript_list:
            is_auto = t.is_generated
            lang_code = t.language_code
            break

    transcript = ytt_api.fetch(video_id, languages=languages)
    segments = transcript.to_raw_data()
    return segments, lang_code or 'unknown', is_auto


def scrape_channel(channel_url: str, limit: int | None, languages: list[str], delay: float, min_duration_secs: int = 1800):
    channel_kwargs = extract_channel_identifier(channel_url)

    print(f"Fetching video list from {channel_url} ...")
    # Note: sort_by='oldest' is broken in scrapetube 2.6.
    # We fetch newest-first (default) and reverse to process oldest-first.
    # When --limit is set, we get the N newest videos (reversed to oldest-first).
    videos = list(scrapetube.get_channel(
        **channel_kwargs,
        content_type='videos',
        limit=limit,
    ))

    if not videos:
        print("No videos found.")
        return

    videos.reverse()  # oldest first for natural wiki buildup
    total = len(videos)
    print(f"Found {total} video(s).")

    # Fetch exact channel metadata via innertube API (one request)
    first_meta = fetch_video_metadata(videos[0]['videoId'])
    channel_display = (
        first_meta['channel_name']
        or get_channel_name_from_video(videos[0])
        or channel_name_from_url(channel_url)
    )
    channel_id = first_meta['channel_id'] or get_channel_id_from_video(videos[0])
    channel_name = sanitize_filename(channel_display)
    channel_dir = RAW_YT_DIR / channel_name
    channel_dir.mkdir(parents=True, exist_ok=True)

    existing_ids = get_existing_video_ids(channel_dir)
    error_file = channel_dir / '_scrape_errors.json'
    ytt_api = YouTubeTranscriptApi()

    scraped = 0
    skipped = 0
    failed = 0
    today = datetime.now().strftime('%Y-%m-%d')

    for i, video in enumerate(videos, 1):
        vid = video['videoId']
        title = get_video_title(video)

        if vid in existing_ids:
            print(f"  [{i}/{total}] SKIP (exists): {title}")
            skipped += 1
            continue

        duration_str = get_video_duration(video)
        duration_secs = parse_duration_seconds(duration_str)
        if min_duration_secs > 0 and duration_secs is not None and duration_secs < min_duration_secs:
            print(f"  [{i}/{total}] SKIP (too short: {duration_str}): {title}")
            skipped += 1
            continue

        print(f"  [{i}/{total}] {title} ({vid})")

        try:
            segments, lang_code, is_auto = fetch_transcript_for_video(ytt_api, vid, languages)
        except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as e:
            print(f"           FAILED: {e}")
            log_scrape_error(error_file, vid, title, str(e))
            failed += 1
            continue
        except Exception as e:
            print(f"           FAILED: {e}")
            log_scrape_error(error_file, vid, title, str(e))
            failed += 1
            continue

        transcript_text = clean_transcript(segments)
        if not transcript_text:
            print("           FAILED: empty transcript")
            log_scrape_error(error_file, vid, title, 'Empty transcript after cleaning')
            failed += 1
            continue

        # Fetch exact publish date via innertube (already-scraped videos were skipped above)
        vid_meta = fetch_video_metadata(vid)
        publish_date = vid_meta['publish_date'] or parse_relative_date(get_publish_date_text(video))
        duration = get_video_duration(video)
        safe_title = sanitize_filename(title)
        filename = f"{safe_title}_{publish_date}_{vid}.md"

        frontmatter = {
            'source_type': 'youtube_video',
            'video_id': vid,
            'title': title,
            'channel': channel_display,
            'channel_id': channel_id,
            'url': f'https://www.youtube.com/watch?v={vid}',
            'publish_date': publish_date,
            'duration': duration,
            'language': lang_code,
            'is_auto_generated': is_auto,
            'ingested_date': today,
            'status': 'raw',
        }

        header = (
            f"# {title}\n\n"
            f"**Channel:** {channel_display}  \n"
            f"**Date:** {publish_date}  \n"
            f"**Duration:** {duration}  \n"
            f"**URL:** https://www.youtube.com/watch?v={vid}"
        )

        write_raw_markdown(channel_dir / filename, frontmatter, header, transcript_text)
        scraped += 1

        if delay > 0 and i < total:
            time.sleep(delay)

    print(f"\nDone. {scraped} scraped, {skipped} skipped (existing), {failed} failed.")


def main():
    parser = argparse.ArgumentParser(description='Scrape YouTube channel transcripts into raw/ markdown files.')
    parser.add_argument('channel_url', help='YouTube channel URL (e.g. https://www.youtube.com/@handle)')
    parser.add_argument('--limit', type=int, default=None, help='Max videos to fetch (default: all)')
    parser.add_argument('--lang', nargs='+', default=['en', 'hi', 'en-IN'], help='Language priority (default: en hi en-IN)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between transcript fetches in seconds (default: 1.0)')
    parser.add_argument('--min-duration', type=int, default=30, help='Minimum video duration in minutes (default: 30). Set to 0 to disable.')
    args = parser.parse_args()

    scrape_channel(args.channel_url, args.limit, args.lang, args.delay, args.min_duration * 60)


if __name__ == '__main__':
    main()
