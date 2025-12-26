import requests
import datetime
import time
import zoneinfo
import csv

# ===========================================================
# "DEFINE"-style toggle: choose "men" or "women"
# ===========================================================
SPORT = "men"   # <-- change to "men" or "women"
# ===========================================================

CENTRAL_TZ = zoneinfo.ZoneInfo("America/Chicago")

def fetch_ncaa_scores(date: datetime.date):
    """Fetch NCAA basketball scores (men's or women's) for the given date from ESPN’s public API."""
    date_str = date.strftime("%Y%m%d")
    sport_path = "mens-college-basketball" if SPORT.lower().startswith("m") else "womens-college-basketball"
    url = (
        "https://site.api.espn.com/apis/site/v2/sports/"
        f"basketball/{sport_path}/scoreboard"
        f"?dates={date_str}&groups=50&limit=300"
    )
    resp = requests.get(url)
    if resp.status_code != 200:
        print(f"Failed to fetch {date_str}: {resp.status_code}")
        return None
    return resp.json()

def parse_games(data_json):
    """Parse ESPN JSON and extract simplified game info with Central Time conversion."""
    if not data_json or "events" not in data_json:
        return []
    games = []
    for event in data_json["events"]:
        comp = event.get("competitions", [{}])[0]
        teams = comp.get("competitors", [])
        if len(teams) < 2:
            continue

        status = comp.get("status", {}).get("type", {}).get("description", "")
        if status.lower() != "final":
            continue

        home = next((t for t in teams if t.get("homeAway") == "home"), teams[0])
        away = next((t for t in teams if t.get("homeAway") == "away"), teams[1])

        # Convert UTC timestamp to Central Time
        utc_dt = datetime.datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
        local_dt = utc_dt.astimezone(CENTRAL_TZ)

        # Extract venue info
        venue = comp.get("venue", {}).get("fullName", "")
        city = comp.get("venue", {}).get("address", {}).get("city", "")
        state = comp.get("venue", {}).get("address", {}).get("state", "")
        location = ", ".join(filter(None, [venue, city, state]))

        games.append({
            "date": local_dt.date().isoformat(),
            "away_team": away.get("team", {}).get("displayName", ""),
            "away_score": away.get("score", ""),
            "home_team": home.get("team", {}).get("displayName", ""),
            "home_score": home.get("score", ""),
            "venue": location,
        })
    return games

def find_season_start(max_search_days=60):
    """Find the first day of the current season that has games."""
    today = datetime.date.today()
    guess_start = datetime.date(today.year if today.month >= 11 else today.year - 1, 11, 1)

    print(f"Searching for first day with {SPORT.title()} NCAA games...")
    for offset in range(max_search_days):
        date = guess_start + datetime.timedelta(days=offset)
        data = fetch_ncaa_scores(date)
        if data and data.get("events"):
            print(f"Season appears to start on {date}")
            return date
        time.sleep(0.2)
    print("⚠️  Could not auto-detect season start — defaulting to November 1.")
    return guess_start

def main():
    now_central = datetime.datetime.now(CENTRAL_TZ)
    today = now_central.date()
    season_start = find_season_start()

    gender_label = "Women's" if SPORT.lower().startswith("w") else "Men's"
    filename = "past_games.csv"

    print(
        f"\nFetching NCAA {gender_label} Basketball results (Central Time) "
        f"from {season_start} to {now_central.strftime('%Y-%m-%d %H:%M:%S %Z')}...\n"
    )

    all_games = []
    current_date = season_start
    while current_date <= today:
        data = fetch_ncaa_scores(current_date)
        games = parse_games(data)
        if games:
            all_games.extend(games)
            print(f"{current_date}: {len(games)} final games found.")
        else:
            print(f"{current_date}: no final games.")
        time.sleep(0.3)
        current_date += datetime.timedelta(days=1)

    print(f"\nTotal final games fetched: {len(all_games)}\n")

    # Show sample output
    for g in all_games[:10]:
        print(
            f"{g['date']} — {g['away_team']} ({g['away_score']}) @ "
            f"{g['home_team']} ({g['home_score']}) — {g['venue']}"
        )

    # Save full season results to CSV (always named past_games.csv)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["date", "away_team", "away_score", "home_team", "home_score", "venue"])
        for g in all_games:
            writer.writerow([
                g["date"],
                g["away_team"],
                g["away_score"],
                g["home_team"],
                g["home_score"],
                g["venue"],
            ])

    print(f"\n✅ Full {gender_label.lower()} results saved to {filename} (entire season, Central Time)")

if __name__ == "__main__":
    main()
