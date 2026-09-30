import pandas as pd
import json

df = pd.read_csv("dataset/flipkart_com-ecommerce_sample.csv")
cols = ["product_name", "product_category_tree", "brand", "retail_price",
        "discounted_price", "product_rating", "description"]
df = df[cols].rename(columns={"product_name": "name", "discounted_price": "price"})

df["category"] = df["product_category_tree"].str.extract(r'\["?([A-Za-z ]+)')
df["category"] = df["category"].str.strip()
df = df.drop(columns=["product_category_tree"])
df = df.dropna(subset=["name", "brand", "price", "category"])

df = df[df["category"].isin(["Jewellery", "Home Decor"])]

top_brands = (
    df.groupby("category")["brand"]
    .apply(lambda s: s.value_counts().head(6).index.tolist())
)
allowed_brands = set(b for brands in top_brands for b in brands)
df = df[df["brand"].isin(allowed_brands)]

def diverse_sample(data, category, per_brand=3, total=10):
    subset = data[data["category"] == category]
    picked = subset.groupby("brand", group_keys=False).head(per_brand)
    return picked.head(total)

selected = pd.concat([
    diverse_sample(df, "Jewellery"),
    diverse_sample(df, "Home Decor"),
])

print("Selected per category:")
print(selected["category"].value_counts())
print("Brands used:")
print(selected.groupby("category")["brand"].unique())

selected["description"] = selected["description"].astype(str).str.slice(0, 150)
selected["rating"] = pd.to_numeric(selected["product_rating"], errors="coerce")
selected = selected.drop(columns=["product_rating"])
selected.insert(0, "id", range(1, len(selected) + 1))

products = selected.to_dict(orient="records")
with open("dataset/products.json", "w", encoding="utf-8") as f:
    json.dump(products, f, indent=2, ensure_ascii=False)

print("Saved", len(products), "products to dataset/products.json")