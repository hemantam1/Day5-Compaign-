# backend.py

import pandas as pd
import numpy as np
from rapidfuzz import fuzz

# ======================
# OOPs BACKEND – POLISHED DEMO
# ======================

class Product:
    def __init__(self, pid, name, brand, category, price, sponsored, keywords, image, campaign_kw):
        self.id = pid
        self.name = name
        self.brand = brand
        self.category = category
        self.price = price
        self.sponsored = sponsored
        self.keywords = keywords
        self.image = image
        self.campaign_kw = campaign_kw  # For demo attribution

class ProductCatalog:
    def __init__(self):
        self.products = []
        self.categories = [
            {"category": "Smartwatch", "folder": "Smartwatch", "keywords": ["smartwatch", "watch", "fitness watch"]},
            {"category": "Wireless Earbuds", "folder": "Wireless_Earbuds", "keywords": ["earbuds", "wireless earbuds", "bluetooth earbuds"]},
            {"category": "Smartphone", "folder": "Smartphone", "keywords": ["mobile", "smartphone", "android phone"]},
            {"category": "Laptop", "folder": "Laptop", "keywords": ["laptop", "notebook", "ultrabook"]},
            {"category": "Tablet", "folder": "Tablet", "keywords": ["tablet", "ipad", "android tablet"]},
            {"category": "Power Bank", "folder": "Power_Bank", "keywords": ["power bank", "portable charger"]},
            {"category": "Gaming Mouse", "folder": "Gaming_Mouse", "keywords": ["gaming mouse", "mouse", "rgb mouse"]},
            {"category": "Headphones", "folder": "Headphones", "keywords": ["headphones", "over ear headphones"]},
            {"category": "Mechanical Keyboard", "folder": "Mechanical_Keyboard", "keywords": ["keyboard", "mechanical keyboard"]},
            {"category": "Bluetooth Speaker", "folder": "Bluetooth_Speaker", "keywords": ["speaker", "bluetooth speaker", "portable speaker"]},
        ]

    def generate_products(self, n=120):
        brands = ["Brand A", "Brand B", "Brand C", "Brand D"]
        for i in range(n):
            cat = np.random.choice(self.categories)
            img_index = np.random.randint(1, 11)
            image_path = f"images/{cat['folder']}/{img_index}.jpg"
            campaign_kw = np.random.choice(cat["keywords"])  # Assign one keyword as demo campaign keyword
            prod = Product(
                pid=i,
                name=f"{cat['category']} Model {i}",
                brand=np.random.choice(brands),
                category=cat["category"],
                price=round(np.random.uniform(50, 500), 2),
                sponsored=np.random.choice(["Yes", "No"], p=[0.35, 0.65]),
                keywords=cat["keywords"],
                image=image_path,
                campaign_kw=campaign_kw
            )
            self.products.append(prod)

    def to_dataframe(self):
        data = []
        for p in self.products:
            data.append({
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "price": p.price,
                "sponsored": p.sponsored,
                "keywords": p.keywords,
                "image": p.image,
                "campaign_kw": p.campaign_kw
            })
        return pd.DataFrame(data)

class SearchEngine:
    def __init__(self, catalog_df, catalog_obj):
        self.df = catalog_df
        self.catalog_obj = catalog_obj

    # Detect category based on query keywords
    def detect_category(self, query):
        query = query.lower()
        for cat in self.catalog_obj.categories:
            for kw in cat["keywords"]:
                if fuzz.partial_ratio(query, kw.lower()) > 70:
                    return cat["category"]
        return None

    # Suggestions based on partial match
    def suggestions(self, text):
        if not text:
            return []
        s = set()
        for kws in self.df["keywords"]:
            for k in kws:
                if fuzz.partial_ratio(text.lower(), k.lower()) > 60:
                    s.add(k)
        return list(s)[:6]

    # Search function returning sponsored first
    def search(self, query):
        target_category = self.detect_category(query)
        df_filtered = self.df
        if target_category:
            df_filtered = df_filtered[df_filtered["category"] == target_category]

        matched = []
        for _, r in df_filtered.iterrows():
            for k in r["keywords"]:
                if fuzz.partial_ratio(query.lower(), k.lower()) > 60:
                    matched.append(r)
                    break

        if not matched:
            return pd.DataFrame()

        results = pd.DataFrame(matched)

        # Sponsored products first
        sponsored_df = results[results["sponsored"] == "Yes"]
        organic_df = results[results["sponsored"] == "No"]

        return pd.concat([sponsored_df, organic_df], ignore_index=True)
