import numpy as np
import pandas as pd
import sys
sys.path.append("..")
def datetime_to_min(time):
    return time.hour*60+time.minute

def get_xlsx_data(path):
    df=pd.read_excel(path)
    time=df.iloc[:,1].to_list()
    df=df.iloc[:,0].str.split('-',expand=True)
    df.columns=['start','end']
    df['start']=pd.to_datetime(df['start'])
    df['start']=df['start'].apply(datetime_to_min)
    point=df['start'].to_list()
    point.append(2000)
    return point,time

# path='data/timetable/嘉定116路上行运营时间.xlsx'
# df,time=get_xlsx_data(path)
# print(df)
# print(time)
# print(len(df))
# print(len(time))