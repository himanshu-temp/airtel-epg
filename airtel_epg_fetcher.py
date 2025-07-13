import requests
from datetime import datetime
import json
import re

HEADERS = {"User-Agent": "Mozilla/5.0"}

# 1. Input your categorized channel list
channel_categories = {
    "Entertainment": [
        "Sony Sab", "Star Plus", "Star Plus HD", "Colors SD", "Colors HD",
        "Star Bharat", "Star Bharat HD", "Dangal", "SONY SAB", "Sony SAB HD",
        "SET HD", "Sony Pal", "Zee TV", "Zee TV HD", "&TV HD", "Zee Anmol"
    ],
    "Movies": [
        "Star Gold", "Star Gold HD", "Star Gold 2", "Star Gold 2 HD", "Star Gold Select",
        "Star Gold Select HD", "Colors Cineplex", "Colors Cineplex HD",
        "Colors Cineplex Superhit", "Colors Cineplex Bollywood", "SONY Max",
        "Sony MAX HD", "Zee Cinema", "Zee Cinema HD", "&Pictures", "&Pictures HD",
        "Zee Bollywood", "Zee Classic"
    ],
    "Kids": [
        "Pogo Hindi", "Disney Channel", "Disney Junior", "Sonic Hindi", "Nick Hindi",
        "Hungama", "Super Hungama", "Cartoon Network Hindi", "Discovery Kids 2", "Sony Yay"
    ],
    "Knowledge": [
        "Discovery Channel Hindi", "History TV18 HD Hindi", "Animal Planet Hindi",
        "Discovery Science", "Sony BBC Earth HD"
    ],
    "Sports": [
        "Star Sports Khel", "Star Sports 1", "Star Sports 1 Hindi HD", "Star Sports 2",
        "Star Sports 2 Hindi", "Star Sports 2 Hindi HD", "Star Sports Select 1",
        "Star Sports Select 1 HD", "Star Sports Select 2", "Star Sports Select 2 HD",
        "Sony TEN 1 SD", "Sony TEN 1 HD", "Sony TEN 2 SD", "Sony TEN 2 HD",
        "Sony TEN 3 SD", "Sony TEN 3 HD", "Sony sports ten 4", "Sony sports ten 4 HD",
        "Sony TEN 5 SD", "Sony TEN 5 HD"
    ],
    "News": [
        "ABP News India", "News 18 India", "DD News", "India TV", "NDTV India",
        "India news", "Aaj Tak", "Zee News"
    ]
}

# 2. Fetch Airtel channel list from their API
def fetch_all_airtel_channels():
    print("Fetching Airtel channel list from API...")
    url = "https://api.airtelxstream.in/play/channels?filter=all&limit=1000"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        raise Exception("Failed to fetch Airtel channel list")
    
    data = res.json()
    lookup = {}
    for ch in data.get("data", []):
        name = ch.get("title", "").strip().lower()
        slug = ch.get("slug", "")
        ch_id = ch.get("id", "")
        if name and slug and ch_id:
            lookup[name] = {"slug": slug, "id": ch_id}
    print(f"Found {len(lookup)} channels.")
    return lookup

# 3. Fetch EPG for a given channel
def get_schedule(slug, ch_id):
    url = f"https://www.airtelxstream.in/livetv-channels/{slug}/schedule/MWTV_LIVETVCHANNEL_{ch_id}"
    res = requests.get(url, headers=HEADERS)
    if res.status_code != 200:
        return []

    match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', res.text)
    if not match:
        return []

    try:
        data = json.loads(match.group(1))
        programmes = list(data["epg"]["programmes"].values())[0]
        return [{
            "title": prog["title"],
            "start": datetime.fromisoformat(prog["startTime"]).strftime("%I:%M %p"),
            "end": datetime.fromisoformat(prog["endTime"]).strftime("%I:%M %p")
        } for prog in programmes]
    except Exception as e:
        return [{"error": str(e)}]

# 4. Main logic
def run_epg_fetch():
    channel_lookup = fetch_all_airtel_channels()
    epg = {}

    for category, channels in channel_categories.items():
        epg[category] = {}
        for name in channels:
            key = name.lower().strip()
            match = channel_lookup.get(key)
            if match:
                print(f"Fetching schedule for: {name}")
                epg[category][name] = get_schedule(match["slug"], match["id"])
            else:
                print(f"Not found on Airtel: {name}")
                epg[category][name] = []

    # Save to JSON
    with open("airtel_epg_full.json", "w", encoding="utf-8") as f:
        json.dump(epg, f, indent=2, ensure_ascii=False)
    print("Saved EPG to airtel_epg_full.json")

# 5. Run the script
if __name__ == "__main__":
    run_epg_fetch()
