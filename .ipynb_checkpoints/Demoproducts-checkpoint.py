import pandas as pd
import numpy as np

# Step 1: Generate 50 dummy products for 2 products
products = ["Smartwatch", "Wireless Earbuds"]
brands = ["Brand A", "Brand B", "Brand C", "Brand D"]

data = []
for i in range(50):
    product = np.random.choice(products)
    brand = np.random.choice(brands)
    price = round(np.random.uniform(50, 200), 2)
    sponsored = np.random.choice(["Yes", "No"], p=[0.3, 0.7])
    data.append([i+1, product + " " + str(i+1), brand, product, price, sponsored])

# Create DataFrame
df = pd.DataFrame(data, columns=["Product_ID","Product_Name","Brand","Category","Price","Sponsored"])

# Optional: save CSV
df.to_csv("dummy_products.csv", index=False)
