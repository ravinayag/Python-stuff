# -*- coding: utf-8 -*-
#/usr/bin/python


import MySQLdb as mdb
import pandas as pd
import numpy as np
from sqlalchemy import *
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime


###Mysql DB

#engine = create_engine('mysql+pymysql://root:password@192.168.1.128/freelancedb1', echo=False)
engine = create_engine('mysql+pymysql://ravinayag:password@localhost/all_data', echo=False)


con = engine.connect()
#cursor = con.cursor()

###DB Query, and import to Dataframe
#query = "select * from datasource where (previous_value OR current_value is not NULL) AND checked = 0"
query = "select * from datasource"      ##### Use this for testing purpose for email
df = pd.read_sql(query, con)


### Apply Arithmetic operation for Margin value and checked column
df['margin_value'] = df['current_value'] / df['previous_value'] -1

def check_col():
    checked = []
    for value in df["margin_value"]:
        if value < 0 or value >= 0:
            checked.append("1")
        else:
            checked.append("0")
    df["checked"] = checked

check_col()
### write to new preprodtable
df.to_sql(name='preprodtable', con=engine, if_exists='replace', index=False)

### update the production  "datasource" table with margin and checked columns only

def db_commit():
    con = engine.connect()
    con.autocommit = false
    with con as cn:
        sql = """UPDATE
                     datasource t1,
                     preprodtable t2
                SET
                     t1.margin_value = t2.margin_value,
                     t1.checked = t2.checked
                WHERE
                     t1.id = t2.id"""
        cn.execute(sql)
        #con.commit()
db_commit()
sql1= """TRUNCATE TABLE preprodtable"""
con.execute(sql1)
con.close()

#### Email Setup

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 465
# Create a secure SSL context
context = ssl.create_default_context()

### Sender details
sender = "mailsender@gmail.com"
password = "hidden"
#password = input("Type your password and press enter: ")

### Recepient details and Text message to type
recipient = "ravinayag@gmail.com, mailsender@gmail.com"
message = 'Hello,  \n Here is the Margin value is less than < -0.25 and No Book_id'


#### Bussiness table logic with condition
df['when_start'] = pd.to_datetime(df['when_start'],unit='s') ### converting from epoch format to datetime format
df['when_start']= pd.DatetimeIndex(df['when_start'])  + pd.DateOffset(hours=2) ### adding two hours from datetime.
mdf1 = df[df.margin_value <= -0.25]
mdf2 = df[df["book_id"].isnull()]
mdf = mdf1.append(mdf2)
mdf.to_html('filename.html', index=False)


def eml():
    msg = MIMEMultipart()
    msg['Subject'] = 'Python email Test for Alberto'
    msg['To'] = recipient
    msg['From'] = 'mailsender@gmail.com'


    ### for Text Message
    part = MIMEText('text', "plain/html")
    part.set_payload(message)
    msg.attach(part)

        ### For html Print, do not change else end up with alignment problem
    html = open('filename.html')
    part2 = MIMEText(html.read(), 'html')
    msg.attach(part2)


    session = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context)
    session.login(sender, password)

    mssg=msg
    session.sendmail(sender, recipient, mssg.as_string())
    session.quit()
    print("email sent")
#if __name__ == '__main__':

######### Telegram Send Notification #########
import telegram_send

mdf = mdf.reset_index()

def tgsend():
        for i in range(len(mdf)) :
                a = mdf.loc[i, "book_id"]
                b = mdf.loc[i, "country"]
                c = mdf.loc[i, "previous_value"]
                d = mdf.loc[i, "current_value"]
                e = mdf.loc[i, "margin_value"]
                f = mdf.loc[i, "when_start"]
                telegram_send.send(messages=["####### Start ####### \n BookId : {}\n Country : {} \n PreviousValue : {}\n CurrentValue : {} \n MarginValue : {} \n WhenStart : {} \n ####### End  ####### ".format(a,b,c,d,e,f)])
                #print ( "Telegram Message sent ")
if len(mdf) > 0:
    eml()
    tgsend()
    print ("Telegram Message sent ")
else :
    print("No email/Telegram Sent")
    #print("No Telegram Message sent")
