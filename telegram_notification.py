-*- coding: utf-8 -*-
#/usr/bin/python

##### Telegram-send has to configure first with your token
### the syntax is $ telegram-send --configure it ask for your token, 
### ref : https://pypi.org/project/telegram-send/

import MySQLdb as mdb
import pandas as pd
import numpy as np
from sqlalchemy import *
import telegram_send
from datetime import datetime

###Mysql DB
engine = create_engine('mysql+pymysql://root:password@localhost/db1', echo=False)

con = engine.connect()
#cursor = con.cursor()

###DB Query, and import to Dataframe
query = "select * from datasource where previous_value OR current_value is not NULL"
df = pd.read_sql(query, con)

### Converting unix timing to datetime format
df['Time_start'] = pd.to_datetime(df['Time_start'],unit='s')
df['odd_timestamp'] = pd.to_datetime(df['odd_timestamp'],unit='s')


### Apply Arithmetic operation for Marginal value and checked column
df['m_value'] = df['current_value'] / df['previous_value'] -1

def check_col():
    checked = [] 
    for value in df["m_value"]:  
        if value < 0 or value >= 0: 
            checked.append("1") 
        else: 
            checked.append("0") 

    df["checked"] = checked    

check_col()
### write to new preprodtable 
df.to_sql(name='preprodtable', con=engine, if_exists='replace', index=False)

### update the production  "datasource" table with marginal value and checked columns only
#con = engine.connect()
#con.autocommit = false
def db_commit():
    con = engine.connect()
    con.autocommit = false
    with con as cn:
        sql = """UPDATE 
                     datasource t1, 
                     preprodtable t2
                SET 
                     t1.m_value = t2.m_value,
                     t1.checked = t2.checked
                WHERE
                     t1.id = t2.id"""

        cn.execute(sql)
        #con.commit()
db_commit()
con.close()

mdf1 = df[df.m_value <= -0.25]
mdf2 = df[df["book_id"].isnull()]
mdf = mdf1.append(mdf2)
mdf = mdf.reset_index()

######### Telegram Send Notification #########

def tgsend():
        for i in range(len(mdf)) :
                a = mdf.loc[i, "book_id"]
                b = mdf.loc[i, "country"]
                c = mdf.loc[i, "previous_value"]
                d = mdf.loc[i, "current_value"]
                e = mdf.loc[i, "m_value"]
                f = mdf.loc[i, "when_start"]
                telegram_send.send(messages=["####### Start ####### \n BookId : {}\n Country : {} \n PreviousValue : {}\n CurrentValue : {} \n MarginValue : {} \n WhenStart : {} \n ####### End  ####### ".format(a,b,c,d,e,f)])
                
if len(mdf) > 0:
    tgsend()
	print ( "Telegram Message sent ")
else :
        print("No Telegram Message sent")

