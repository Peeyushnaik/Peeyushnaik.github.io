"""Fetch live Instagram numbers and write them to data/stats.json for the portfolio.

Uses the official Instagram API (Instagram Login). Needs one environment variable:
  IG_ACCESS_TOKEN   long-lived Instagram user access token (see SETUP-AUTO-STATS.md)

Optional:
  IG_TOKEN_OUT      if set, the script refreshes the token (long-lived tokens expire after
                    60 days) and writes the new one to this file path, so the workflow can
                    save it back as a GitHub secret.
  REEL_SAMPLE       how many recent reels to average views over (default 12)

Only the Python standard library is used, so nothing needs installing.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://graph.instagram.com/v21.0"
OUT_FILE = Path(__file__).resolve().parent.parent / "data" / "stats.json"
MIN_REEL_AGE = timedelta(days=2)  # brand-new reels are still collecting views, so skip them


def get(url: str, **params) -> dict:
    query = urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(f"{url}?{query}", timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        body = err.read().decode("utf-8", "replace")
        # Never print the token: strip it from any echoed URL.
        raise SystemExit(f"Instagram API error {err.code}: {body[:500]}") from None


def reel_views(media_id: str, token: str) -> int | None:
    data = get(f"{API}/{media_id}/insights", metric="views", access_token=token).get("data", [])
    if not data:
        return None
    item = data[0]
    if "total_value" in item:
        return int(item["total_value"].get("value", 0))
    values = item.get("values") or [{}]
    return int(values[0].get("value", 0))


def main() -> None:
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        raise SystemExit("IG_ACCESS_TOKEN is not set.")
    sample = int(os.environ.get("REEL_SAMPLE", "12"))

    profile = get(f"{API}/me", fields="username,followers_count,media_count", access_token=token)

    media = get(f"{API}/me/media", fields="id,media_product_type,timestamp", limit=50, access_token=token)
    now = datetime.now(timezone.utc)
    views = []
    for item in media.get("data", []):
        if item.get("media_product_type") != "REELS":
            continue
        posted = datetime.fromisoformat(item["timestamp"].replace("+0000", "+00:00"))
        if now - posted < MIN_REEL_AGE:
            continue
        v = reel_views(item["id"], token)
        if v is not None:
            views.append(v)
        if len(views) >= sample:
            break

    stats = {
        "username": profile.get("username"),
        "followers": int(profile["followers_count"]),
        "posts": int(profile["media_count"]),
        "avg_views": round(sum(views) / len(views)) if views else 0,
        "reels_sampled": len(views),
        "top_recent_reel_views": max(views) if views else 0,
        "updated_at": now.isoformat(timespec="seconds"),
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(f"followers={stats['followers']} posts={stats['posts']} "
          f"avg_views={stats['avg_views']} over {stats['reels_sampled']} reels")

    token_out = os.environ.get("IG_TOKEN_OUT")
    if token_out:
        refreshed = get("https://graph.instagram.com/refresh_access_token",
                        grant_type="ig_refresh_token", access_token=token)
        new_token = refreshed.get("access_token")
        if new_token:
            Path(token_out).write_text(new_token, encoding="utf-8")
            print("Token refreshed.")
        else:
            print("Token refresh returned no token; keeping the old one.", file=sys.stderr)


if __name__ == "__main__":
    main()
