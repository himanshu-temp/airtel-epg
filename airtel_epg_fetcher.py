import xml.etree.ElementTree as ET
import requests
import io

# Step 1: Download the EPG XML
print("Downloading EPG...")
url = "https://epg.pw/xmltv/epg_IN.xml"
response = requests.get(url)
if response.status_code != 200:
    raise Exception(f"Failed to fetch EPG: {response.status_code}")
data = response.content

# Step 2: Parse it
print("Parsing XML...")
tree = ET.parse(io.BytesIO(data))
root = tree.getroot()

# Step 3: Define desired channels
keep = {
    "Sony TEN 1", "Sony TEN 1 HD", "Sony TEN 2", "Sony TEN 2 HD",
    "Sony TEN 3", "Sony TEN 3 HD", "Sony Sports TEN 4", "Sony Sports TEN 4 HD",
    "Sony TEN 5", "Sony TEN 5 HD",
    "SONY SAB", "Sony SAB HD", "SET HD", "Sony Pal",
    "SONY Max", "Sony MAX HD", "Sony Yay", "Sony BBC Earth HD",
    "Zee TV", "Zee TV HD", "&TV HD", "Zee Anmol",
    "Zee Cinema", "Zee Cinema HD", "&Pictures", "&Pictures HD",
    "Zee Bollywood", "Zee Classic", "Aaj Tak", "Zee News"
}

# Normalize names (some entries may lack "HD"/"SD" in display-name)
def match_channel(display_names):
    for name in display_names:
        name_lower = name.lower().replace("sd", "").replace("hd", "").strip()
        for target in keep:
            if name_lower in target.lower():
                return True
    return False

# Step 4: Filter <channel> tags
print("Filtering channels...")
channel_ids = set()
for chan in root.findall('channel'):
    display_names = [d.text.strip() for d in chan.findall('display-name') if d.text]
    if match_channel(display_names):
        channel_ids.add(chan.get('id'))
    else:
        root.remove(chan)

# Step 5: Filter <programme> tags
print("Filtering programmes...")
for prog in root.findall('programme'):
    if prog.get('channel') not in channel_ids:
        root.remove(prog)

# Step 6: Save filtered EPG
print("Saving filtered_epg.xml")
tree.write('filtered_epg.xml', encoding='utf-8', xml_declaration=True)

print("✅ Done.")
