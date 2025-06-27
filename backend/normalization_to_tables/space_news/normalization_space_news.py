import pandas as pd

def normalize(input_file):
    df=pd.read_csv(input_file)
    news_articles_table=["title","url","content","postexcerpt"]
    publishing_info_table=["title","author",'date']
    news_articles_df=df[news_articles_table]
    publishing_info_df=df[publishing_info_table]
    news_articles_df.to_csv("news_articles_table.csv",index=False)
    publishing_info_df.to_csv("publishing_info.csv",index=False)
    print("data split successfully !")


input_file = r'spacenews.csv'  
normalize(input_file)