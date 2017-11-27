import tushare as ts
import datetime
import pandas as pd

info=ts.get_stock_basics()
highlist =pd.DataFrame({"date":"","open":"","high":"","close":"","low":"","volume":"","amount":""},index=["0"])

def loop_all_stocks():
    days = 60
    count =0
    for EachStockID in info.index:
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=days*7/5
        start_day=end_day-datetime.timedelta(days)
        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        df= ts.get_h_data(EachStockID,start=start_day,end=end_day)
        if not(df is None):
            period_high=df['high'].max()
            today_high=df.iloc[0]['high']
            if today_high>=period_high:
                highlist.append(df,ignore_index=True)
                count+=1

if __name__ == '__main__':
    loop_all_stocks()
    print("a new high list",highlist)
