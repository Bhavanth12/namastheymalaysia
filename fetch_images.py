import os
import json
import urllib.request
import urllib.parse
import re

places = ["Batu Caves", "George Town, Penang", "Malacca City", "Thean Hou Temple", "Kek Lok Si", "Sarawak Cultural Village", "Islamic Arts Museum Malaysia", "Sultan Abdul Samad Building", "Sri Mahamariamman Temple, Kuala Lumpur", "Kampung Baru, Kuala Lumpur"]
foods = ["Nasi lemak", "Char kway teow", "Laksa", "Roti canai", "Satay", "Hainanese chicken rice", "Bak kut teh", "Cendol", "Rendang", "Hokkien mee"]
festivals = ["Thaipusam", "Hari Raya Aidilfitri", "Chinese New Year", "Diwali", "Gawai Dayak", "Kaamatan", "Vesak", "Mid-Autumn Festival", "Rainforest World Music Festival", "Chingay parade"]

original_names = {
    "George Town, Penang": "George Town",
    "Malacca City": "Melaka Historic City",
    "Kek Lok Si": "Kek Lok Si Temple",
    "Islamic Arts Museum Malaysia": "Islamic Arts Museum",
    "Sri Mahamariamman Temple, Kuala Lumpur": "Sri Mahamariamman Temple",
    "Kampung Baru, Kuala Lumpur": "Kampung Baru",
    "Nasi lemak": "Nasi Lemak",
    "Char kway teow": "Char Kway Teow",
    "Roti canai": "Roti Canai",
    "Hainanese chicken rice": "Hainanese Chicken Rice",
    "Bak kut teh": "Bak Kut Teh",
    "Rendang": "Beef Rendang",
    "Hokkien mee": "Hokkien Mee",
    "Diwali": "Deepavali",
    "Vesak": "Wesak Day",
    "Mid-Autumn Festival": "Mooncake Festival",
    "Chingay parade": "Penang Chingay"
}

image_map = {}

def get_image(title):
    url = f"https://en.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(title)}&prop=pageimages&format=json&pithumbsize=800"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) NamastheyBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            pages = data['query']['pages']
            for page_id in pages:
                if 'thumbnail' in pages[page_id]:
                    return pages[page_id]['thumbnail']['source']
    except Exception as e:
        print(f"Failed for {title}: {e}")
    return None

print("Fetching images from Wikipedia...")
for cat in [places, foods, festivals]:
    for item in cat:
        orig = original_names.get(item, item)
        img_url = get_image(item)
        if img_url:
            image_map[orig] = img_url
        else:
            print(f"No image found for {item}")

# Fallbacks for items that might not have a clean main thumbnail on wiki
fallbacks = {
    "Sri Mahamariamman Temple": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Sri_Mahamariamman_Temple_KL_1.jpg/800px-Sri_Mahamariamman_Temple_KL_1.jpg",
    "Kampung Baru": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7b/Kampung_Baru_Skyline_KL.jpg/800px-Kampung_Baru_Skyline_KL.jpg",
    "Rainforest World Music Festival": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/RWMF_2019_Crowd.jpg/800px-RWMF_2019_Crowd.jpg",
    "Beef Rendang": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Rendang_daging_sapi_asli_Minang.JPG/800px-Rendang_daging_sapi_asli_Minang.JPG",
    "Hari Raya Aidilfitri": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Eid_al-Fitr_prayer_in_Jakarta.jpg/800px-Eid_al-Fitr_prayer_in_Jakarta.jpg",
    "Gawai Dayak": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/Dayak_people_in_traditional_clothing.jpg/800px-Dayak_people_in_traditional_clothing.jpg",
    "Kaamatan": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Sumazau_Dance_Sabah.jpg/800px-Sumazau_Dance_Sabah.jpg"
}

for k, v in fallbacks.items():
    if k not in image_map or not image_map[k]:
        image_map[k] = v

with open('image_map.json', 'w') as f:
    json.dump(image_map, f, indent=4)
print("Saved image config to image_map.json")

# Now update all HTML files
import glob

# For replacing in main lists and sub pages
# Regex to match image tags
img_pattern = re.compile(r'<img src="(.*?)" alt="(.*?)" class="post-img"(.*?)>')
recent_img_pattern = re.compile(r'<img src="(.*?)" alt="(.*?)" class="recent-img"(.*?)>')
activity_pattern = re.compile(r'<img src="(.*?)" alt="(.*?)" class="img-main"(.*?)>')

def replacer(match):
    src = match.group(1)
    alt = match.group(2)
    rest = match.group(3)
    
    # Try to find alt in image_map
    if alt in image_map and image_map[alt]:
        new_src = image_map[alt]
        return f'<img src="{new_src}" alt="{alt}" class="post-img"{rest}>'
    return match.group(0)

# Replace recent img (batu caves, nasi lemak)
def recent_replacer(match):
    src = match.group(1)
    alt = match.group(2)
    rest = match.group(3)
    
    # Normally alt is 'Thumb', so we need context. But wait, in recent posts we know what they are.
    # The recent posts are Batu Caves and Nasi Lemak
    return match.group(0) # we will do a manual replace for recent posts

for file in glob.glob("*.html"):
    with open(file, "r", encoding='utf-8') as f:
        content = f.read()
    
    # Replace main post images
    content = img_pattern.sub(replacer, content)

    # For recent posts, replace statically since the alt was "Thumb"
    if "Batu Caves" in image_map:
        content = re.sub(r'<img src="[^"]*" alt="Thumb" class="recent-img">\s*<div class="recent-info">\s*<span>STANDARD &nbsp;•&nbsp; MAY 14, 2026</span>\s*<h4>Batu Caves</h4>',
                         f'<img src="{image_map["Batu Caves"]}" alt="Batu Caves" class="recent-img">\n                        <div class="recent-info">\n                            <span>STANDARD &nbsp;•&nbsp; MAY 14, 2026</span>\n                            <h4>Batu Caves</h4>', content)
    
    if "Nasi Lemak" in image_map:
        content = re.sub(r'<img src="[^"]*" alt="Thumb" class="recent-img">\s*<div class="recent-info">\s*<span>STANDARD &nbsp;•&nbsp; MAY 14, 2026</span>\s*<h4>Nasi Lemak</h4>',
                         f'<img src="{image_map["Nasi Lemak"]}" alt="Nasi Lemak" class="recent-img">\n                        <div class="recent-info">\n                            <span>STANDARD &nbsp;•&nbsp; MAY 14, 2026</span>\n                            <h4>Nasi Lemak</h4>', content)

    # Also fix index activity images
    if file == "index.html":
        content = content.replace('<img src="https://images.unsplash.com/photo-1541359927273-d76820fc43f9?auto=format&fit=crop&w=800&q=80" alt="Resort" class="img-main">', 
                                  f'<img src="{image_map.get("Batu Caves", "")}" alt="Resort" class="img-main">')
        content = content.replace('<img src="https://images.unsplash.com/photo-1533383401166-5b42e7d77a83?auto=format&fit=crop&w=600&q=80" alt="Sunset" class="img-offset">', 
                                  f'<img src="{image_map.get("Nasi Lemak", "")}" alt="Sunset" class="img-offset">')
                                  
    # In index about section, update profile pic
    if file == "about.html":
        content = content.replace('src="https://images.unsplash.com/photo-1518684079-3c830dcef090?auto=format&fit=crop&w=600&q=80" alt="Profile"', 
                                  'src="https://upload.wikimedia.org/wikipedia/commons/thumb/0/03/Petronas_Towers_KLCC_2020.jpg/800px-Petronas_Towers_KLCC_2020.jpg" alt="Profile"')

    # In sub pages, the hero image is static teal but wait, they don't have hero images, just color
    
    with open(file, "w", encoding='utf-8') as f:
        f.write(content)
print("HTML generated.")
