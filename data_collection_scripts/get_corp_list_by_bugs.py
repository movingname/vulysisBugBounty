import os
from pymongo import Connection
import codecs

con = Connection()
db = con.wooyun_2
bugs = db.bugs


file_corp_url_list = '../data/corp_list.txt'
file_corp_url_list_unreg = '../data/corp_list_unreg.txt'

known_url_corp_set = []

if os.path.isfile(file_corp_url_list):
    f_list = codecs.open(file_corp_url_list, 'r', "utf-8")
    for line in f_list:
        known_url_corp_set.append(line.split(',')[0])
    f_list.close()
else:
    print("ERROR: should obtain corp_url_list.txt from Wooyun first.")

f_unreg = codecs.open(file_corp_url_list_unreg, "w", "utf-8")

for bug in bugs.find():
    if bug['corp'] not in known_url_corp_set:
        known_url_corp_set.append(bug['corp'])
        f_unreg.write(bug['corp'] + "\n")
        
f_unreg.close()