import pandas as pd
import numpy as np
import streamlit as st
from rapidfuzz import fuzz
import os



products = ["Smartwatch", "Wireless Earbuds"]
brands = ["Brand A", "Brand B", "Brand C", "Brand D"]

data = []

watch_counter = 1
earbuds_counter = 1

for i in range(50):
    product = np.random.choice(products)
    brand = np.random.choice(brands)
    price = round(np.random.uniform(50, 200), 2)
    sponsored = np.random.choice(["Yes", "No"], p=[0.3, 0.7])

    if product == "Smartwatch":
        image_path = f"images/Smartwatch{watch_counter}.jpg"
        watch_counter += 1
        if watch_counter > 25: watch_counter = 1
        keywords = ["smartwatch", "watch", "digital watch", "fitness watch", "smart watch"]
        sponsored_keywords = ["smartwatch for men", "fitness watch", "watch under 200"]
    else:
        image_path = f"images/earbuds{earbuds_counter}.jpg"
        earbuds_counter += 1
        if earbuds_counter > 25: earbuds_counter = 1
        keywords = ["earbuds", "wireless earbuds", "bluetooth earbuds", "earphones"]
        sponsored_keywords = ["wireless earbuds for gym", "bluetooth earbuds"]

    data.append([
        i + 1,
        f"{product} {i+1}",
        brand,
        product,
        price,
        sponsored,
        image_path,
        keywords,
        sponsored_keywords
    ])

df = pd.DataFrame(
    data,
    columns=[
        "Product_ID",
        "Product_Name",
        "Brand",
        "Category",
        "Price",
        "Sponsored",
        "Image",
        "Keywords",
        "Sponsored_Keywords"
    ]
)


try:
    df.to_csv("dummy_products.csv", index=False)
except PermissionError:
    st.warning("Cannot save CSV (file open or permission denied)")



def match_query(query, keyword_list):
    query = query.lower()
    for kw in keyword_list:
        score = fuzz.partial_ratio(query, kw.lower())
        if score >= 70:
            return True
    return False

def search_products_with_filters(query, min_price=0, max_price=500):
    query = query.lower()
    sponsored_results = []
    normal_results = []

    
    if "watch" in query:
        target_category = "Smartwatch"
    elif "earbuds" in query or "earphone" in query:
        target_category = "Wireless Earbuds"
    else:
        target_category = None  

    for _, row in df.iterrows():
        
        if not (min_price <= row["Price"] <= max_price):
            continue
        
        if target_category and row["Category"] != target_category:
            continue

       
        if row["Sponsored"] == "Yes" and (
            match_query(query, row["Keywords"]) or match_query(query, row["Sponsored_Keywords"])
        ):
            sponsored_results.append(row)
   
        elif match_query(query, row["Keywords"]) or match_query(query, row["Sponsored_Keywords"]):
            normal_results.append(row)

   
    if len(sponsored_results) + len(normal_results) == 0:
        fallback_sponsored = df[df["Sponsored"] == "Yes"].sample(min(5, len(df[df["Sponsored"] == "Yes"])))
        fallback_normal = df.sample(min(5, len(df)))
        results = pd.concat([fallback_sponsored, fallback_normal], ignore_index=True)
    else:
        results = pd.DataFrame(sponsored_results + normal_results)

    return results

# Streamlit

st.set_page_config(page_title="Sponsored Product Search Demo", layout="centered")

st.title("Compaign Demo")
# st.write("Search products with fuzzy match and price filter. Sponsored products always top!")


query = st.text_input("🔍 Search for a product (e.g. Smartwatch)")


min_price, max_price = st.slider(
    "Filter by price range ($)",
    min_value=0,
    max_value=500,
    value=(0, 200)
)

if query:
    results = search_products_with_filters(query, min_price, max_price)

    if results.empty:
        st.warning("No products found.")
    else:
        for _, row in results.iterrows():
            col1, col2 = st.columns([1, 3])
            with col1:
                if os.path.exists(row["Image"]):
                    st.image(row["Image"], width=120)
                else:
                    st.write("No Image")
            with col2:
                st.subheader(row["Product_Name"])
                st.write(f"**Brand:** {row['Brand']}")
                st.write(f"**Price:** ${row['Price']}")
                if row["Sponsored"] == "Yes":
                    st.markdown("🟨 **SPONSORED**")
            st.divider()
