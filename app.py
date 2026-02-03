import streamlit as st
import os
import glob
import numpy as np
import pandas as pd
from backend import ProductCatalog, SearchEngine

# ======================
# PAGE CONFIG
# ======================
st.set_page_config(page_title="Amazon Sponsored Demo", layout="wide")

# ======================
# CSS
# ======================
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
}
.product-name {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    display: block;
}
</style>
""", unsafe_allow_html=True)

# ======================
# 🔒 CATALOG – SESSION LOCK (MOST IMPORTANT FIX)
# ======================
if "catalog" not in st.session_state:
    catalog = ProductCatalog()
    catalog.generate_products()
    st.session_state.catalog = catalog
else:
    catalog = st.session_state.catalog

df = catalog.to_dataframe()
engine = SearchEngine(df, catalog)

# ======================
# UI
# ======================
st.title("🛒 Amazon-Style Sponsored Product Demo")

# Search
query = st.text_input("Search products", placeholder="Search laptop, smartwatch, earbuds...")

# Suggestions
if query:
    suggestions = engine.suggestions(query)
    if suggestions:
        cols_s = st.columns(len(suggestions))
        for i, s in enumerate(suggestions):
            if cols_s[i].button(s):
                query = s

# Results
results = df.copy()
if query:
    results = engine.search(query)
    if results.empty:
        st.info("No products found")

# ======================
# PRODUCT GRID
# ======================
if not results.empty:
    st.markdown("### 🛍 Products")
    cols = st.columns(4)

    for i, row in results.iterrows():
        with cols[i % 4]:
            st.markdown("<div class='card'>", unsafe_allow_html=True)

            # Image
            category_folder = row["category"].replace(" ", "_")
            folder_path = os.path.join("images", category_folder)
            images = []
            for ext in ("*.jpg", "*.jpeg", "*.png"):
                images.extend(glob.glob(os.path.join(folder_path, ext)))

            if images:
                st.image(np.random.choice(images), width=200)
            else:
                st.image("https://via.placeholder.com/200", width=200)

            # Details
            st.markdown(
                f"<span class='product-name' title='{row['name']}'>{row['name']}</span>",
                unsafe_allow_html=True
            )
            st.write(row["brand"])
            st.markdown(f"<div class='price'>${row['price']}</div>", unsafe_allow_html=True)

            if row["sponsored"] == "Yes":
                st.markdown("<div class='sponsored'>Sponsored</div>", unsafe_allow_html=True)

            # ✅ CORRECT BUY LINK (product_id locked)
            checkout_url = f"/checkout?product_id={row['id']}"
            st.markdown(
                f'<a href="{checkout_url}" target="_blank"><button>🛒 Buy</button></a>',
                unsafe_allow_html=True
            )

            st.markdown("</div>", unsafe_allow_html=True)
