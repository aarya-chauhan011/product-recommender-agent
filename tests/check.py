import pandas as pd

df = pd.read_csv("flipkart_com-ecommerce_sample.csv")
df["top_cat"] = df["product_category_tree"].str.extract(r'\["?([A-Za-z ]+)')
print(df["top_cat"].value_counts().head(15))