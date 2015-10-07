from pymongo import Connection
import codecs

con = Connection()
db = con.wooyun_2
corps = db.corps

#f_rank = open("corp_rank.csv", "r")

#rank_map = {}

#for line in f_rank:
#    strs = line.split(',')
#    rank_map[strs[0]] = strs[1]

f_corp = codecs.open("../data/corp_list.txt", "r", "utf-8")

for line in f_corp:
    corp_item = {}
    strs = line.split(',')
    #corp_item["registration_time"] = strs[0]
    corp_item["name"] = strs[0]
    corp_item["url"] = strs[1].strip()
    #corp_item["alexa_rank"] = int(rank_map[strs[2]])
    corps.insert(corp_item)
