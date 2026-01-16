from flask import Flask, request, jsonify
import pandas as pd
import os
from update_dataset_with_images import add_fallback_images_if_needed

app = Flask(__name__)

DATASET_PATH = 'description.csv'
IMAGE_FOLDER = 'images'


def load_dataset():
    df = pd.read_csv(DATASET_PATH)
    # strip spaces
    df = df.apply(lambda col: col.map(lambda x: x.strip() if isinstance(x, str) else x))

    # 🔹 Make sure column names are clean and consistent
    df.columns = [c.strip() for c in df.columns]

    # If someone ever changes CSV to "color", we still support it
    if "color" in df.columns and "colour" not in df.columns:
        df = df.rename(columns={"color": "colour"})

    return df


@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.json or {}

    # Safely read input
    item_name = data.get('item_name', '').strip().lower()
    color = data.get('color', 'any').strip().lower()

    if not item_name:
        return jsonify({"error": "item_name is required"}), 400

    # Load dataset
    df = load_dataset()

    # Normalize item_name + colour in dataframe
    if 'item_name' not in df.columns:
        return jsonify({"error": "Dataset missing 'item_name' column"}), 500
    if 'colour' not in df.columns:
        return jsonify({"error": "Dataset missing 'colour' column"}), 500

    df['item_name'] = df['item_name'].astype(str).str.lower()
    df['colour'] = df['colour'].astype(str).str.lower()

    # Filter by item_name
    filtered = df[df['item_name'] == item_name]

    # Filter by color (using 'colour' column)
    if color != 'any':
        filtered = filtered[filtered['colour'] == color]

    # If nothing found → use fallback scraping
    if filtered.empty:
        add_fallback_images_if_needed(item_name, color)

        df = load_dataset()
        if 'item_name' not in df.columns or 'colour' not in df.columns:
            return jsonify({"recommendations": [], "message": "No outfits found (invalid dataset format after fallback)."}), 200

        df['item_name'] = df['item_name'].astype(str).str.lower()
        df['colour'] = df['colour'].astype(str).str.lower()

        filtered = df[df['item_name'] == item_name]
        if color != 'any':
            filtered = filtered[filtered['colour'] == color]

    if filtered.empty:
        return jsonify({'recommendations': [], 'message': 'No outfits found.'})

    results = filtered.sample(min(5, len(filtered))).to_dict(orient='records')
    return jsonify({'recommendations': results})


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
