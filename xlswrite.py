import cx_Oracle
import mysql.connector
import pandas as pd
import openpyxl

#### Which DB has to run the Query type by oracle or none to mysql(default to mysql)
DB = 'oracle1'

if DB is 'oracle' :
####Oracle DB
    db = cx_Oracle.connect('scott/tiger@localhost:port/service') 
    cursor = db.cursor() 
else: 
####Mysql DB
    db = mysql.connector.connect(host="localhost", user="root", passwd="password", db="campus")    
    cursor = db.cursor()
   
###### Your sql Query
query = "SELECT id, firstname, lastname, gender, dob, country, reg_num, status, campus_id, blood_group FROM student WHERE gender='F'"

df = pd.read_sql(query, db)
def add_text(row):
    return row + "+Addtxt"     #### You can add your own text here
df['firstname1'] = df['firstname'].apply(add_text)  #### you can choose your own column(Ex. district_id) and new column name
df[['campus_id', 'id']]= df[['campus_id', 'id']].astype(str)  #### converting from INT to String

### writing to excel sheet
writer = pd.ExcelWriter('c:\PyProjects\ML\output.xlsx', engine='openpyxl', converters={'id':str,'campus_id':str})
df.to_excel(writer, "Sheet1", index=False)
writer.save()
cursor.close()
