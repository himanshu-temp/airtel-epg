import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import re

# Channel name + schedule page URL
CHANNELS = {
    "India TV": "https://www.airtelxstream.in/livetv-channels/india-tv/schedule/MWTV_LIVETVCHANNEL_10000000000910000",
    "Republic Bharat": "https://www.airtelxstream.in/livetv-channels/republic-tv-bharat/schedule/MWTV_LIVETVCHANNEL_10000000063500000",
    "News Nation": "https://www.airtelxstream.in/livetv-channels/news-nation/schedule/MWTV_LIVETVCHANNEL_254"
    # Add more channels if needed
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_schedule(url):
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    script_tag = soup.find("script", string=re.compile("__INITIAL_STATE__"))
    if not script_tag:
        return []

    try:
        raw_json = re.search(r"window\.__INITIAL_STATE__\s*=\s*({.*?});", script_tag.string).group(1)
        data = json.loads(raw_json)
        # extract the first schedule list
        programme_list = list(data['epg']['programmes'].values())[0]

        return [
            {
                "title": prog["title"],
                "start": datetime.fromisoformat(prog["startTime"]).strftime("%I:%M %p"),
                "end": datetime.fromisoformat(prog["endTime"]).strftime("%I:%M %p")
            }
            for prog in programme_list
        ]
    except Exception as e:
        return [{"error": str(e)}]

# Fetch all schedules
epg_data = {}
for name, url in CHANNELS.items():
    print(f"Fetching schedule for: {name}")
    epg_data[name] = get_schedule(url)

# Save to JSON file
with open("airtel_schedule.json", "w", encoding="utf-8") as f:
    json.dump(epg_data, f, indent=2, ensure_ascii=False)

print("✅ Schedule saved to airtel_schedule.json")
