from pymongo import MongoClient
import codecs
import operator
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

fontSize = 18
figWidth = 7
figHeight = 5
sectorDistPath= '../fig/sector_dist.pdf'

blackList = ["CCERT教育网应急响应组", "cncert国家互联网应急中心"]

sectors = ["edu", "gov", "finance", "media", "travel",
           "entertainment", "health", "food", "trans", "comm",
           "manufactoring", "energy", "email", "mobile", "gaming",
           "social", "video", "security", "hr", "cms", "portal",
           "forum", "ecommerce", "browser", "office", "information"]

it_sectors = [ "comm","email", "mobile", "gaming", "social", "video", "security", "hr", 
              "cms", "portal", "forum", "ecommerce", "browser", "office",
              "information"]

sector_full = {"edu":"Education", "gov":"Government", "finance":"Finance",
               "media":"Media", "travel":"Travel \& Hotel",
               "entertainment":"Entertainment", "health":"Healthcare",
               "food":"Food \& Drink", "trans":"Transportation",
               "comm":"Telecomm.", "manufactoring":"Manufactoring",
               "energy":"Energy \& Utilities", "email":"Email",
               "mobile":"Mobile", "gaming":"Gaming", "social":"Social Networks",
               "video":"Video \& Photo", "security":"Security", "cms":"CMS",
               "portal":"Portal", "forum":"Forum", "ecommerce":"E-commerce",
               "browser":"Browser", "hr":"HR", "office":"Office",
               "information":"Information"}

con = MongoClient()
db = con.wooyun_2
bugs = db.bugs
           
sector_file = {}

for sector in sectors:
    sector_file[sector] = codecs.open("../data/corp_category_round_1/corp_" + sector + ".txt", 'r', 'utf-8')

sector_corp = {}
corp_sector = {}

sector_bugs = {}
it_sector_bugs = {}
nonit_sec_bugs = {}

for sector in sectors:
    
    sector_corp[sector] = []
    sector_bugs[sector] = 0
    if sector in it_sectors:
        it_sector_bugs[sector] = 0
    else:
        nonit_sec_bugs[sector] = 0
        
    for line in sector_file[sector]:
        corp = line.strip().split(",")[0]
        sector_corp[sector].append(corp)
        if corp in corp_sector:
            # TODO: These are actually duplicates. Need to merge.
            print("WARNING: corp " + corp + " belongs to multiple sectors!")
            print("Old sector: " + corp_sector[corp] + ", new sector: " + sector)
        corp_sector[corp] = sector
        
    sector_file[sector].close()          

blackListCount = 0
for bug in bugs.find():
    corp = bug["corp"]

    if corp in blackList:
        blackListCount += 1
        continue

    if corp not in corp_sector:
        continue

    sector_bugs[corp_sector[corp]] += 1     
    
    if corp_sector[corp] in it_sectors:
        it_sector_bugs[corp_sector[corp]] += 1
    else:
        nonit_sec_bugs[corp_sector[corp]] += 1

print("blackListCount = " + str(blackListCount))

print("IT sectors:")
print(it_sector_bugs)
print("\n")
print("non IT sectors:")
print(nonit_sec_bugs)

sector_sorted = []
sector_bugs_sorted = []

for pair in sorted(nonit_sec_bugs.items(), key=operator.itemgetter(1), reverse=True):
    sector_sorted.append(sector_full[pair[0]])
    sector_bugs_sorted.append(pair[1])

#sector_sorted.append("")
#sector_bugs_sorted.append(0)



for pair in sorted(it_sector_bugs.items(), key=operator.itemgetter(1), reverse=True):
    
    if pair[0] == "email":
        continue
    
    sector_sorted.append(sector_full[pair[0]])
    sector_bugs_sorted.append(pair[1])

print(sector_bugs_sorted)

pos = np.arange(0, len(sector_sorted))

fig_sector_dist = plt.figure()

ax = fig_sector_dist.add_subplot(111)

# ax.set_ylabel('Count', fontsize=fontSize)

#sector_bugs_sorted.insert(0, max(sector_bugs_sorted))

plt.bar(pos, sector_bugs_sorted, edgecolor ="b", fill=False)

#sector_bugs_sorted.remove(max(sector_bugs_sorted))

plt.xticks(np.arange(0, len(sector_sorted), 1),
           sector_sorted, rotation=270)


plt.tick_params(axis='both', which='major', labelsize=14)
#fig_sector_dist.set_size_inches(figWidth, figHeight + 3)

fig_sector_dist.tight_layout()

fig_sector_dist.savefig(sectorDistPath)

