
import os
import csv
from icrawler.builtin import GoogleImageCrawler

DATASET_PATH = 'description.csv'
IMAGE_FOLDER = 'images'

def add_fallback_images_if_needed(item_name, color='any'):
    query = f"{color} {item_name}" if color.lower() != 'any' else item_name
    crawler = GoogleImageCrawler(storage={'root_dir': IMAGE_FOLDER})
    crawler.crawl(keyword=query, max_num=5)

    # Get the latest downloaded images
    files = sorted(os.listdir(IMAGE_FOLDER), key=lambda x: os.path.getctime(os.path.join(IMAGE_FOLDER, x)), reverse=True)[:5]

    # Add new rows to the dataset
    with open(DATASET_PATH, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for filename in files:
            writer.writerow([item_name, color, '', filename])




