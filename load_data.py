import pandas as pd


def load_data():
    df1 = pd.read_csv("afli_data1.csv")
    df2 = pd.read_csv("afli_data2.csv")
    df3 = pd.read_csv("afli_data3.csv")

    afli_df = pd.concat([df1, df2, df3], ignore_index=True)

    return afli_df