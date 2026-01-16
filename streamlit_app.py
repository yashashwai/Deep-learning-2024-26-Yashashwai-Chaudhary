# streamlit_app.py
import streamlit as st
import requests
import os
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(page_title="Fashion Outfit Recommender", layout="centered")
st.title("👗 AI-Powered Fashion Outfit Recommender")

# Config
API_URL = "http://127.0.0.1:5000/recommend"
IMAGES_FOLDER = "images"  # images should be stored here (relative to where you run Streamlit)
PLACEHOLDER_SIZE = (600, 600)

def make_placeholder_image(text: str, size=PLACEHOLDER_SIZE) -> Image.Image:
    img = Image.new("RGB", size, color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf",20)
    except Exception:
        font = ImageFont.load_default()
    # split long text to multiple lines
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len((cur + " " + w).strip()) > 30:
            lines.append(cur.strip())
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    # draw centered
    total_h = sum(draw.textbbox((0,0), ln, font=font)[3] - draw.textbbox((0,0), ln, font=font)[1] + 6 for ln in lines)
    y = (size[1] - total_h) // 2
    for ln in lines:
        bbox = draw.textbbox((0,0), ln, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        draw.text(((size[0]-w)/2, y), ln, fill=(40,40,40), font=font)
        y += h + 6
    return img

def display_item_image(item: dict):
    caption = item.get("description") or item.get("Description") or ""
    # prefer image_url if backend provided one
    image_url = item.get("image_url")
    image_name = (item.get("image_name") or "").strip()

    # 1) If backend returned an external URL, try it first
    if image_url:
        try:
            st.image(image_url, caption=caption, width="stretch")
            return
        except Exception:
            pass

    # 2) Try local path inside images folder
    if image_name:
        local_path = os.path.join(IMAGES_FOLDER, image_name)
        if os.path.exists(local_path):
            try:
                st.image(local_path, caption=caption, width="stretch")
                return
            except Exception:
                pass

    # 3) Fallback: show placeholder
    placeholder = make_placeholder_image(image_name or "no-image")
    st.image(placeholder, caption=f"{caption}  (placeholder for: {image_name})", width="stretch")

# --- UI ---
st.markdown("Tell us about yourself and the occasion, and we’ll suggest the perfect outfit!")

gender = st.selectbox("Select Gender", ["Female", "Male", "Unisex"])
age = st.selectbox("Select Age", ["young", "teen", "adult", "old"])
weather = st.selectbox("Select Weather", ["summer", "winter", "all", "any"])
item_name = st.text_input("Clothing Category (e.g., dress, t-shirt, jeans):")
color = st.text_input("Preferred Color (or type 'Any'):")

if st.button("✨ Get Recommendations"):
    if not item_name or item_name.strip() == "":
        st.error("Please enter an item_name (e.g., 't-shirt', 'jeans', 'dress').")
    else:
        user_input = {
            "gender": gender.lower(),
            "age": age.lower(),
            "weather": weather.lower(),
            "item_name": item_name.lower().strip(),
            "color": color.lower().strip()
        }

        with st.spinner("Fetching recommendations..."):
            try:
                resp = requests.post(API_URL, json=user_input, timeout=15)
            except requests.exceptions.RequestException as e:
                st.error(f"Request failed: {e}")
                st.stop()

            st.write("HTTP status:", resp.status_code)

            # parse JSON safely
            try:
                data = resp.json()
            except Exception:
                st.error("Backend returned a non-JSON response:")
                st.text(resp.text)
                st.stop()

            # surface backend error message if present
            if isinstance(data, dict) and data.get("error"):
                st.error(f"Backend error: {data.get('error')}")
                if data.get("trace"):
                    st.text(data.get("trace"))
                st.stop()

            # show recommendations
            if "recommendations" in data and data["recommendations"]:
                st.success("Here are your outfit recommendations:")
                for item in data["recommendations"]:
                    display_item_image(item)

            elif "fallback" in data and data["fallback"]:
                st.warning("No exact matches found. Showing fallback results from Google Images.")
                for item in data["fallback"]:
                    display_item_image(item)
            else:
                st.info("No recommendations found. Try a different item_name or color.")
                st.write("Backend response:", data)
