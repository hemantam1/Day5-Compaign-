import streamlit as st
import os
import glob
import numpy as np
import pandas as pd
from backend import ProductCatalog, SearchEngine


# PAGE CONFIG

st.set_page_config(page_title="Amazon Sponsored Demo", layout="wide")


# CSS 

st.markdown("""
<style>
.card {
    border: 1px solid #ddd;
    border-radius: 14px;
    padding: 12px;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    margin-bottom: 16px;
    transition: transform 0.2s, box-shadow 0.2s;
    text-align: center;
}
.card:hover {
    transform: scale(1.03);
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
}
.price { 
    color: #B12704; 
    font-size: 18px; 
    font-weight: bold; 
    margin-top: 4px;
}
.sponsored {
    background:#f0c14b;
    padding:4px 8px;
    border-radius:20px;
    font-size:12px;
    display:inline-block;
    font-weight:bold;
    margin-bottom:6px;
}
button {
    background-color: #ff9900;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    cursor: pointer;
    font-weight: bold;
    margin-top: 8px;
    transition: background-color 0.2s;
}
button:hover {
    background-color: #e68a00;
}
.product-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
}
</style>
""", unsafe_allow_html=True)


# GENERATE DATA

catalog = ProductCatalog()
catalog.generate_products()
df = catalog.to_dataframe()
engine = SearchEngine(df, catalog)

# STREAMLIT UI

st.title("🛒 Amazon-Style Sponsored Product Demo")


# Search Input

query = st.text_input("Search products", placeholder="Search laptop, smartwatch, earbuds...")


# Dynamic Suggestions

if query:
    suggestions = engine.suggestions(query)
    if suggestions:
        st.caption("Suggestions:")
        cols_s = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            if cols_s[i].button(s):
                query = s


# Search Results

results = df.copy()
if query:
    search_results = engine.search(query)
    if not search_results.empty:
        results = search_results
    else:
        results = pd.DataFrame()  # No match


# Product Display (Dynamic Grid + Uniform Images)

if not results.empty:
    st.markdown("### 🛍 Products")
    num_cols = min(4, len(results))
    cols = st.columns(num_cols)

    for i, row in results.iterrows():
        col = cols[i % num_cols]
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # Robust Image Loading
            category_folder = row["category"].replace(" ", "_")
            base_path = os.path.join(os.getcwd(), "images")
            folder_path = os.path.join(base_path, category_folder)
            available_images = []
            for ext in ["*.jpg", "*.jpeg", "*.png"]:
                available_images.extend(glob.glob(os.path.join(folder_path, ext)))

            if available_images:
                image_path = np.random.choice(available_images)
                if os.path.exists(image_path):
                    st.image(image_path, width=200)
                else:
                    st.image("https://via.placeholder.com/200", width=200)
            else:
                st.image("https://via.placeholder.com/200", width=200)

            # Product Details with tooltip
            st.markdown(f"<span class='product-name' title='{row['name']}'>{row['name']}</span>", unsafe_allow_html=True)
            st.write(row["brand"])
            st.markdown(f"<div class='price'>${row['price']}</div>", unsafe_allow_html=True)

            # Sponsored Badge
            if row["sponsored"] == "Yes":
                st.markdown("<div class='sponsored'>Sponsored</div>", unsafe_allow_html=True)

            # Buy Button → open checkout in new tab (multi-page)
            checkout_url = f"/Checkout?product_id={row['id']}"  # must match pages/Checkout.py
            st.markdown(f'<a href="{checkout_url}" target="_blank"><button>🛒 Buy</button></a>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)
