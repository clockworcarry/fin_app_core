import pandas as pd
import datetime

df = pd.read_csv("/home/ghelie/AlgoTrading/FinApp/smp_earnings.csv")
df['Date'] =  pd.to_datetime(df['Date'], format='%Y-%m-%d')

res = []

for idx, row in df.iterrows():
    eps = row['Value']

    dt = row['Date'] - datetime.timedelta(days=365)
    
    prev_year_val = None


    tmp_df = df[df['Date'] >= dt]
    if not tmp_df.empty:
        prev_year_val = tmp_df['Value'].iloc[-1]

    if prev_year_val is not None and prev_year_val > (row['Value'] * 1.25):
        res.append(row['Date'])

print(len(res))
print(res)
