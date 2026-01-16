import os
import requests
from googleapiclient.discovery import build

# Replace with your actual API Key and CSE ID
GCS_DEVELOPER_KEY = 'AIzaSyDfreHd4gBf4c0xuKDn5hzhc78SCiAgI3U'
GCS_CX = '063cd4c891da14f1e'

# Create a service object
service = build("customsearch", "v1", developerKey=GCS_DEVELOPER_KEY)

def fetch_image(query, save_dir="images", img_name=None):
    try:
        res = service.cse().list(
            q=query,
            cx=GCS_CX,
            searchType='image',
            num=1,
            safe='high'
        ).execute()

        if 'items' not in res:
            print("❌ No image results for:", query)
            return None

        image_url = res['items'][0]['link']
        print(f"✅ Found image: {image_url}")

        os.makedirs(save_dir, exist_ok=True)
        img_data = requests.get(image_url).content

        filename = img_name if img_name else query.replace(" ", "_") + ".jpg"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, 'wb') as f:
            f.write(img_data)

        print(f"📥 Saved image to: {file_path}")
        return file_path

    except Exception as e:
        print("⚠️ Error fetching image:", e)
        return None
