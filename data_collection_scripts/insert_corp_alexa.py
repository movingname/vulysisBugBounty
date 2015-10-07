from pymongo import Connection
import sys
sys.path.append('../lib/')
import wooyun_lib
import codecs

con = Connection()
db = con.wooyun_2
reports = db.corp_reports
db_corp_alexa = db.corp_alexa

f_alexa = codecs.open('../data/url_alexa.txt', 'r', 'utf-8')
f_corp_url_list = codecs.open('../data/corp_url_list.txt', 'r', 'utf-8')
f_no_alexa_corp = codecs.open('../data/no_alexa_corp.txt', 'w', 'utf-8')

url_list = []

corp_url = {}

url_alexa = {}

num_corp_url_pair = 0

for line in f_corp_url_list:
    strs = line.split('\t')
    corp = strs[0]
    url = strs[1]

    url = wooyun_lib.normalize(url)	
	
    if url not in url_list:	
        url_list.append(url)

    corp_url[corp] = url
    
    num_corp_url_pair += 1

print("num_corp_url_pair: " + str(num_corp_url_pair))

num_url_alexa_pair = 0

for line in f_alexa:
    strs = line.split(',')
    url = strs[0]
    alexa = int(strs[1])
    
    url_alexa[url] = alexa
    
    num_url_alexa_pair += 1

print("num_url_alexa_pair: " + str(num_url_alexa_pair))

# Insert into Mongodb

num_no_alexa_url = 0

for report in reports.find():
    corp = report['corp']

    if corp == "":
        continue

    alexa = None
    if corp not in corp_url:
        print("WARNING: corp " + corp + " is missing in the corp_url file.")
    else:
        url = corp_url[corp]
        if url in url_alexa:
            alexa = url_alexa[url]
        else:
            num_no_alexa_url += 1
            f_no_alexa_corp.write(corp + "\t" + url + "\n")
            

    item = {}
    item['corp'] = corp
    item['alexa'] = alexa
    
    db_corp_alexa.insert(item)

print("num_no_alexa_url: " + str(num_no_alexa_url))

f_no_alexa_corp.close()