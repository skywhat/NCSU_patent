from __future__ import print_function

import mysql.connector
from mysql.connector import errorcode

import urllib
import urllib2
from bs4 import BeautifulSoup

DB_NAME="patent"

config={
        'user':'root',
        'password':'xxxxxx',
}


'''
fname="1.html"
soup=BeautifulSoup(open(fname),"html.parser")

wanted=soup.select(".technology")
cnt=len(wanted)

urls=[]
url="http://licensing.research.ncsu.edu"
for i in range(cnt):
    urls.append(url+wanted[i].a['href'])

for u in urls:
    print u


'''
def get_info(url):
    response=urllib2.urlopen(url)
    soup=BeautifulSoup(response.read(),"html.parser")
    title=soup.select("#nouvant-portfolio-header")[0].h1.string
    patent_id=soup.select("#nouvant-portfolio-header")[0].em.string.lstrip("Technology #")
    
    r=soup.select(".inventor")
    cnt=len(r)
    researchers=[]
    for i in range(cnt):
        researchers.append((r[i].a.string).encode('utf-8'))
    
    m=soup.select(".manager")
    cnt=len(m)
    manager=[]
    for i in range(cnt):
        manager.append((m[i].a.string).encode('utf-8'))

    res={}
    res["patent_id"]=(patent_id).encode('utf-8')
    res["title"]=(title).encode('utf-8')
    res["inventors"]=researchers
    res["manager"]=manager
    return res

def get_urls(fname):
    soup=BeautifulSoup(open(fname),"html.parser")

    wanted=soup.select(".technology")
    cnt=len(wanted)

    urls=[]
    url="http://licensing.research.ncsu.edu"
    for i in range(cnt):
        urls.append(url+wanted[i].a['href'])
    return urls

def create_database(cursor):
    try:
        cursor.execute(
            "CREATE DATABASE IF NOT EXISTS {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        exit(1)

    try:
        cnx.database = DB_NAME  
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor)
            cnx.database = DB_NAME
        else:
            print(err)
            exit(1) 


def create_table(cursor):
    TABLES={}
    TABLES['patent']=(
            "CREATE TABLE  `patent` ("
            " `patent_id` varchar(20) NOT NULL,"
            " `title` varchar(1024) NOT NULL,"
            " `inventor` varchar(256) NOT NULL,"
            " `manager` varchar(256) "
            ") ")
    for name,ddl in TABLES.iteritems():
        try:
            print("Creating table {}: ".format(name),end='')
            cursor.execute(ddl)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")
    #cursor.close()
    #cnx.close()

if __name__=='__main__':
    cnx=mysql.connector.connect(**config)
    try:
        cnx = mysql.connector.connect(**config)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        cursor=cnx.cursor()
        create_database(cursor)
        create_table(cursor)
        add_patent=("INSERT INTO patent"
                "(patent_id,title,inventor,manager)"
                "VALUES (%s, %s, %s, %s)")
        add_patent_no_manager=("INSERT INTO patent"
                "(patent_id,title,inventor)"
                "VALUES (%s, %s, %s)")
        fname1="1.html"
        urls=get_urls(fname1)
        fname2="2.html"
        urls2=get_urls(fname2)
        urls=urls+urls2
        total_length=len(urls)
        i=0.0
        for u in urls:
            print (str(i/total_length*100)+"% done.")
            i=i+1.0
            res=get_info(u)
            for inventor in res['inventors']:
                if not res['manager']:
                    data_patent=(res['patent_id'],res['title'],inventor)
                    cursor.execute(add_patent_no_manager,data_patent)
                else:
                    data_patent=(res['patent_id'],res['title'],inventor,res['manager'][0])
                    cursor.execute(add_patent,data_patent)
                cnx.commit()
        print("Done!!!")
        cnx.close()



