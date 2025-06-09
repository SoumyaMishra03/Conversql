import pandas as pd

def split_product_dataset(input_csv_file):
    df = pd.read_csv(input_csv_file)
    df.columns = df.columns.str.strip()

    products_table = ['Uniq Id','Category','Product Title','Product Description','Brand','Pack Size Or Quantity','Image Urls']
    pricing_table = ['Uniq Id','Mrp','Price','Offers','Combo Offers']
    availability_table = ['Uniq Id','Site Name','Stock Availibility','Product Asin']

    products_df = df[products_table]
    pricing_df = df[pricing_table]
    availability_df = df[availability_table]

    products_df.to_csv('products_table.csv', index=False)
    pricing_df.to_csv('pricing_table.csv', index=False)
    availability_df.to_csv('availability_table.csv', index=False)

    print("Data has been split into multiple CSV files.")

input_csv_file = r'C:\Users\hbhan\OneDrive\Desktop\programming\internship\Talk2DB\csv\home_sdf_marketing_sample_for_amazon_in-ecommerce__20191001_20191031__30k_data.csv'
split_product_dataset(input_csv_file)
