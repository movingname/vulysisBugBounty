from pymongo import Connection
import codecs
import operator

con = Connection()
db = con.wooyun_2
bugs = db.bugs

bug_type_count = {}

for bug in bugs.find():
    if 'bug_type' in bug:
        if not bug['bug_type'] in bug_type_count:
            bug_type_count[bug['bug_type']] = 0
        bug_type_count[bug['bug_type']] += 1
    else:
        print("Warning: bug has no type!")
    

f = codecs.open("../data/bug_type_freq.csv", "w", "utf-8")

for bug_type in sorted(bug_type_count.items(), key=operator.itemgetter(1), reverse=True):
    f.write(bug_type[0] + "," + str(bug_type[1]) + "\n")

f.close()
