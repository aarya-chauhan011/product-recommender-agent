import pandas as pd

df = pd.read_csv("flipkart_com-ecommerce_sample.csv")
df["top_cat"] = df["product_category_tree"].str.extract(r'\["?([A-Za-z ]+)')

for cat in ["Clothing", "Jewellery", "Footwear", "Watches", "Home Decor"]:
    print("---", cat, "---")
    subset = df[df["top_cat"].str.contains(cat, na=False, case=False)]
    print(subset["brand"].value_counts().head(10))
    print()