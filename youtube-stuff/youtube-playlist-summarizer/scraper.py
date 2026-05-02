#!/usr/bin/env python3
import csv
import os
import re
from urllib.parse import urlparse, parse_qs

import requests
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    raise ValueError("Missing YOUTUBE_API_KEY in .env file")


def safe_filename(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[^\w\s.-]", "", value)
    value = re.sub(r"\s+", "-", value)
    value = re.sub(r"-+", "-", value)
    return value[:150]


def extract_playlist_id(url_or_id: str) -> str:
    value = url_or_id.strip()

    # If it's already just an ID
    if "youtube.com" not in value and "youtu.be" not in value:
        return value

    parsed = urlparse(value)
    query = parse_qs(parsed.query)

    playlist_id = query.get("list", [None])[0]

    if not playlist_id:
        raise ValueError("Could not extract playlist ID (missing list= in URL)")

    return playlist_id


def youtube_get(endpoint: str, params: dict) -> dict:
    url = f"https://www.googleapis.com/youtube/v3/{endpoint}"

    params = {
        **params,
        "key": API_KEY,
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise RuntimeError(data["error"])

    return data


def get_playlist_info(playlist_id: str) -> dict:
    data = youtube_get("playlists", {
        "part": "snippet",
        "id": playlist_id,
        "maxResults": 1,
    })

    items = data.get("items", [])
    if not items:
        raise ValueError("Playlist not found or not accessible")

    snippet = items[0]["snippet"]

    return {
        "playlist_title": snippet.get("title", "Playlist"),
        "channel_title": snippet.get("channelTitle", "Channel"),
    }


def get_playlist_items(playlist_id: str):
    rows = []
    page_token = None

    while True:
        params = {
            "part": "snippet",
            "playlistId": playlist_id,
            "maxResults": 50,
        }

        if page_token:
            params["pageToken"] = page_token

        data = youtube_get("playlistItems", params)

        for item in data.get("items", []):
            snippet = item["snippet"]
            resource = snippet.get("resourceId", {})
            video_id = resource.get("videoId", "")

            rows.append({
                "position": snippet.get("position", ""),
                "title": snippet.get("title", "").strip(),
                "description": " ".join(snippet.get("description", "").splitlines()).strip(),
                "url": f"https://www.youtube.com/watch?v={video_id}" if video_id else "",
            })

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    return rows


def main():
    playlist_input = input("Enter YouTube playlist URL or ID: ").strip()

    playlist_id = extract_playlist_id(playlist_input)

    print(f"Fetching playlist info for: {playlist_id}")
    info = get_playlist_info(playlist_id)

    print("Fetching videos...")
    rows = get_playlist_items(playlist_id)

    channel_name = safe_filename(info["channel_title"])
    playlist_name = safe_filename(info["playlist_title"])

    outfile = f"{channel_name}-{playlist_name}.csv"

    with open(outfile, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["position", "title", "description", "url"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone.")
    print(f"Videos: {len(rows)}")
    print(f"File: {outfile}")


if __name__ == "__main__":
    main()
