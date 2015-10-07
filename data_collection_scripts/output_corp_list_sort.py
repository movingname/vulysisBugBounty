from pymongo import Connection
import codecs
import operator
f_corp_list_sort = codecs.open("../data/corp_list_sort.txt", 'w', 'utf-8')

con = Connection()
db = con.wooyun_2
bugs = db.bugs

corps = []

corp_bug = {}
    
for bug in bugs.find():
    corp = bug["corp"]
    if corp not in corp_bug:
        corp_bug[corp] = 0
    corp_bug[corp] += 1

for pair in sorted(corp_bug.items(), key=operator.itemgetter(1), reverse=True):
    f_corp_list_sort.write(pair[0] + "," + str(pair[1]) + "\n")


f_corp_list_sort.close()
