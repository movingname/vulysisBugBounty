##################################################
#
# This script compares head group and tail group in several aspect.
#
##################################################

import codecs
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import operator
from libwooyun import alexa_levels, fit_powerlaw, last_skip_month, severities, sev_colors, shortenBugType, wh_black_list
from pymongo import Connection
from operator import itemgetter

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

num__prod_group = 3

fontSize = 18
figWidth = 7
figHeight = 5

con = Connection()
db = con.wooyun_2
whitehats = db.whitehats
bugs = db.bugs
bug_type_translation = db.bug_type_translation
corp_alexa = db.corp_alexa

data_folder = "../data/"
whContriPath = "../fig/wh_contri_dist.pdf"
bugTypeDistPath = "../fig/head_tail_type_sev.pdf"

whConFile = codecs.open("../data/whConH1.txt", "r", "utf-8")

f_evp_bug_count_monthly = open(data_folder + 'evp_bug_count_monthly.csv', 'w')
f_evp_bug_type = open(data_folder + 'evp_bug_type.csv', 'w')
f_evp_threat_level_monthly = open(data_folder + 'evp_threat_level_monthly.csv', 'w')
f_evp_alexa_count = open(data_folder + 'evp_alexa_count.csv', 'w')


total_bug = 0
wh_bug = {}

skippedBugCount = 0

for bug in bugs.find():
    wh = bug["whitehat"]
    
    if wh in wh_black_list:
        skippedBugCount += 1
        continue
    
    total_bug += 1
    if wh not in wh_bug:
        wh_bug[wh] = 0
    wh_bug[wh] += 1

print("Total bug number = " + str(total_bug))
print("skippedBugCount = " + str(skippedBugCount))

# We separate white hats into different productivity groups

accumulation = 0

prod_groups_name = {0:"Prod_Low", 1:"Prod_Medium", 2:"Prod_High"}

prod_groups = []
prod_groups_bug_count = []
for i in range(0, num__prod_group):
    prod_groups.append([])
    prod_groups_bug_count.append(0)


for wh_pair in sorted(wh_bug.items(), key=itemgetter(1)):
    accumulation += wh_pair[1]
    for i in range(1, num__prod_group + 1):
        if accumulation <= total_bug * i / num__prod_group:
            prod_groups[i - 1].append(wh_pair[0])
            prod_groups_bug_count[i - 1] += wh_pair[1]
            break

for i in range(0, num__prod_group):
    print(prod_groups_name[i] + " size = " + str(len(prod_groups[i])) + ", bug num = " + str(prod_groups_bug_count[i]))



total_bug_h1 = 0
wh_bug_h1 = {}

for line in whConFile:
    wh = line.strip().split(",")[0]
    bug_count= int(line.strip().split(",")[1])
    wh_bug_h1[wh] = bug_count
    total_bug_h1 += bug_count

print("total_bug_h1: " + str(total_bug_h1))






wh_sorted = []
bug_count_sorted = []

oneTimeCount = 0

for pair in sorted(wh_bug.items(), key=itemgetter(1), reverse=True):
    if pair[0] == "路人甲":
        continue
    wh_sorted.append(pair[0])
    bug_count_sorted.append(pair[1])
    
    if pair[1] == 1:
        oneTimeCount += 1
    
print("The top 1 " + wh_sorted[0] + " has found: " + str(max(bug_count_sorted)))
print("The top 100 has found: " + str(sum(bug_count_sorted[0:100])))
print("oneTimeCount: " + str(oneTimeCount))

wh_sorted_h1 = []
bug_count_sorted_h1 = []

for pair in sorted(wh_bug_h1.items(), key=itemgetter(1), reverse=True):
    wh_sorted_h1.append(pair[0])
    bug_count_sorted_h1.append(pair[1])


#######################################
# Draw the wh bug count distribution
#######################################

fit_wh_contri = plt.figure()

ax = fit_wh_contri.add_subplot(111)

ax.set_xlabel('White hat ranked', fontsize=fontSize)
ax.set_ylabel('Vulnerability Count (log)', fontsize=fontSize)

isLogLog = True

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')


# For log graph, the x start should be 1!
p1 = plt.plot(np.arange(1, len(bug_count_sorted) + 1), bug_count_sorted)
p2 = plt.plot(np.arange(1, len(bug_count_sorted_h1) + 1),
              bug_count_sorted_h1, linestyle="--", color='r')

#p1 = plt.scatter(np.arange(len(bug_count_sorted)), bug_count_sorted)
#p2 = plt.scatter(np.arange(len(bug_count_sorted_h1)),
#              bug_count_sorted_h1)


plt.legend( (p1[0], p2[0]), ('Wooyun', 'HackerOne\_P') )
plt.tick_params(axis='both', which='major', labelsize=14)

# TODO: make these numbers automatically generated. len(elite)
# Remember, the vertical extent is in axes coords
# See: http://stackoverflow.com/questions/11864975/a-bug-in-axvline-of-matplotlib
plt.axvline(x=len(prod_groups[2]), ymin=0.52, ymax=0.65)
plt.axvline(x=len(prod_groups[1]), ymin=0.33, ymax=0.46)

#plt.axhline(y=70, xmin = 0.46, xmax = 0.52)
#plt.axhline(y=16, xmin = 0.27, xmax = 0.4)

fit_wh_contri.tight_layout()

fit_wh_contri.savefig(whContriPath) 






fit_powerlaw(bug_count_sorted)






# Then we compare them using different statistics


month_list = []

prod_group_bug_monthly = []

prod_group_bug_type_count = []

prod_group_alexa_count = []

prod_group_severity_monthly = []

prod_group_severity_count = []

prod_group_corp = []

prod_group_alexa_sev = []

prod_group_sev_type_sorted = []

prod_group_sev_type_percentage_sorted = []

for i in range(0, num__prod_group):
    
    prod_group_bug_monthly.append({})   
    prod_group_bug_type_count.append({})   
    prod_group_corp.append([])   
    prod_group_alexa_sev.append({})   
    prod_group_sev_type_sorted.append({})   
    prod_group_sev_type_percentage_sorted.append({})   
    
    prod_group_alexa_count.append({})   
    for level in alexa_levels:    
        prod_group_alexa_count[i][level] = 0
    
    prod_group_severity_monthly.append({})   
    prod_group_severity_count.append({})   
    for level in severities:
        prod_group_severity_monthly[i][level] = {}
        prod_group_severity_count[i][level] = 0


for bug in bugs.find().sort('submit_time', 1):
    
    submit_month = bug['submit_time'][:7]
    wh = bug['whitehat']
    corp = bug['corp']
    
    if wh in wh_black_list:
        continue
    
    corp_severity = None    
    if 'corp_threat_level' in bug and bug['corp_threat_level'] in severities:
        corp_severity = bug['corp_threat_level']
    else:
        corp_severity = bug['self_threat_level']


    if submit_month == last_skip_month:
        continue

    if not submit_month in month_list:
        month_list.append(submit_month)
        for i in range(0, num__prod_group): 
            prod_group_bug_monthly[i][submit_month] = 0

            for level in severities:
                prod_group_severity_monthly[i][level][submit_month] = 0

    b_type_eng = ""
    b_type = bug['bug_type'].strip()
    translation = bug_type_translation.find_one({'Chinese': b_type})
    if translation != None:
        b_type_eng = translation['English']
        b_type_eng = b_type_eng.strip()
        b_type_eng = shortenBugType(b_type_eng)
    else:
        continue #Skip bug_type without a translation, because they are not significant
    
    if b_type_eng not in prod_group_bug_type_count[0]:
        
        for i in range(0, num__prod_group): 
            prod_group_bug_type_count[i][b_type_eng] = 0
            prod_group_alexa_sev[i][b_type_eng] = {}

            for alexa_level in alexa_levels:
                prod_group_alexa_sev[i][b_type_eng][alexa_level] = {}

                for severity in severities:
                    prod_group_alexa_sev[i][b_type_eng][alexa_level][severity] = 0

    alexa_group = ""
    corp_alexa_pair = corp_alexa.find_one({'corp': bug['corp']})

    if corp_alexa_pair != None and corp_alexa_pair['alexa'] != None:
        alexa = corp_alexa_pair['alexa']
        if alexa <= 200:
            alexa_group = alexa_levels[0]
        elif alexa <= 2000:
            alexa_group = alexa_levels[1]
        else:
            alexa_group = alexa_levels[2]
    else:
        alexa_group = alexa_levels[2]


    for i in range(0, num__prod_group):
        if wh in prod_groups[i]:
            prod_group_bug_monthly[i][submit_month] += 1
            if b_type_eng != "":
                prod_group_bug_type_count[i][b_type_eng] += 1
            prod_group_severity_count[i][corp_severity] += 1
            prod_group_severity_monthly[i][corp_severity][submit_month] += 1
            prod_group_alexa_count[i][alexa_group] += 1
            prod_group_alexa_sev[i][b_type_eng][alexa_group][corp_severity] += 1
            prod_group_bug_type_count[i][b_type_eng] += 1
            if corp not in prod_group_corp[i]:
                prod_group_corp[i].append(corp)
            break

for i in range(0, num__prod_group):
    print(prod_groups_name[i] + " org size = " + str(len(prod_group_corp[i])))




bug_type_name_sorted = []

for pair in sorted(prod_group_bug_type_count[i].items(),
                   key=operator.itemgetter(1), reverse=True):
    bug_type_name_sorted.append(pair[0])



for i in range(0, num__prod_group):
    for severity in severities:  
        prod_group_sev_type_sorted[i][severity] = []
        for type_name in bug_type_name_sorted:
            prod_group_sev_type_sorted[i][severity].append(0)
            for alexa_level in alexa_levels:
                prod_group_sev_type_sorted[i][severity][len(prod_group_sev_type_sorted[i][severity]) - 1] += prod_group_alexa_sev[i][type_name][alexa_level][severity]


for i in range(0, num__prod_group):
    for severity in severities:  
        prod_group_sev_type_percentage_sorted[i][severity] = []

        for j in range(0, len(bug_type_name_sorted)):
            total = 0
            for _severity in severities:
                total += prod_group_sev_type_sorted[i][_severity][j]
            prod_group_sev_type_percentage_sorted[i][severity].append(prod_group_sev_type_sorted[i][severity][j] / total)

#print(public_sev_type_percentage_sorted["高"])

########################################################
# Draw bug type severity distribution of different groups
########################################################


pos = np.arange(len(bug_type_name_sorted))
width = 0.35     # gives histogram aspect to the bar diagram

fig_bug_type = plt.figure()

ax = fig_bug_type.add_subplot(111)

# TODO: add space between bar groups

plts = []
for i in range(0, num__prod_group):
    p1 = plt.bar(pos + width * i, prod_group_sev_type_percentage_sorted[i]["低"], width,
               color=sev_colors["低"])

    p2 = plt.bar(pos + width * i, prod_group_sev_type_percentage_sorted[i]["中"], width,
                 color=sev_colors["中"], bottom=prod_group_sev_type_percentage_sorted[i]["低"])  

    p3 = plt.bar(pos + width * i, prod_group_sev_type_percentage_sorted[i]["高"], width,
                 color=sev_colors["高"], bottom=[prod_group_sev_type_percentage_sorted[i]["低"][j] +prod_group_sev_type_percentage_sorted[i]["中"][j] for j in range(len(bug_type_name_sorted))])  


plt.legend((p1[0], p2[0], p3[0]), ('Low', 'Medium', 'High'),
             loc='upper center', bbox_to_anchor=(0.5, 1.10),
          ncol=3, fancybox=True, shadow=True )

ax.set_xticks(pos + width)
plt.xticks(np.arange(0, len(bug_type_name_sorted), 1),
           bug_type_name_sorted, rotation=270)



fig_bug_type.set_size_inches(figWidth, figHeight)

fig_bug_type.tight_layout()

fig_bug_type.savefig(bugTypeDistPath)

sum_percent = {}
for severity in severities:
    sum_percent[severity] = 0

for i in range(0, num__prod_group):
    for severity in severities: 
        percent = prod_group_severity_count[i][severity] / prod_groups_bug_count[i]
        print(prod_groups_name[i] + " severity (with in) " + severity + ": " + str(percent))
        sum_percent[severity] += percent

for i in range(0, num__prod_group):
    for severity in severities: 
        percent = prod_group_severity_count[i][severity] / prod_groups_bug_count[i]
        print(prod_groups_name[i] + " severity (cross) " + severity + ": " + str(percent / sum_percent[severity]))

sum_percent = {}
for level in alexa_levels: 
    sum_percent[level] = 0

for i in range(0, num__prod_group):
    for level in alexa_levels:    
        percent = prod_group_alexa_count[i][level]  / prod_groups_bug_count[i]
        print(prod_groups_name[i] + " alexa (with in) " + level + ": " + str(percent))
        sum_percent[level] += percent

for i in range(0, num__prod_group):
    for level in alexa_levels:    
        percent = prod_group_alexa_count[i][level]  / prod_groups_bug_count[i]
        print(prod_groups_name[i] + " alexa (cross) " + level + ": " + str(percent / sum_percent[level]))


#f_evp_bug_count_monthly.write("month,elite,public\n")
#f_evp_threat_level_monthly.write(("month,elite_high,elite_med,elite_low,public_high,public_med,public_low\n"))
#
#for month in month_list:
#    f_evp_bug_count_monthly.write(month + "," + str(elite_bug_monthly[month]) + "," + str(public_bug_monthly[month]) + "\n")
#    f_evp_threat_level_monthly.write(month + ",")
#    
#     
#    
#    f_evp_threat_level_monthly.write(str(elite_threat_level_monthly["高"][month]) + ",")
#    f_evp_threat_level_monthly.write(str(elite_threat_level_monthly["中"][month]) + ",")
#    f_evp_threat_level_monthly.write(str(elite_threat_level_monthly["低"][month]) + ",")
#    f_evp_threat_level_monthly.write(str(public_threat_level_monthly["高"][month]) + ",")
#    f_evp_threat_level_monthly.write(str(public_threat_level_monthly["中"][month]) + ",")
#    f_evp_threat_level_monthly.write(str(public_threat_level_monthly["低"][month]) + "\n")
#
#    for level in threat_levels:   
#        elite_threat_count[level] += elite_threat_level_monthly[level][month]
#        public_threat_count[level] += public_threat_level_monthly[level][month]






#f_evp_bug_type.write("type,elite,public\n")
#
#for bug_type in elite_bug_type_count:
#    f_evp_bug_type.write('\"' + bug_type  +'\",\"' + str(elite_bug_type_count[bug_type] / elite_bug_total) + '\",\"' + str(public_bug_type_count[bug_type] / public_bug_total) + '\"\n')

#elite_alexa_total = 0
#public_alexa_total = 0
#for level in alexa_levels:
#    elite_alexa_total += elite_alexa_count[level]
#    public_alexa_total += public_alexa_count[level]


#f_evp_alexa_count.write("title,elite,public\n")
#for level in alexa_levels:
#    f_evp_alexa_count.write(level + ",")
#    f_evp_alexa_count.write(str(elite_alexa_count[level] / elite_alexa_total) + ",")
#    f_evp_alexa_count.write(str(public_alexa_count[level] / public_alexa_total) + "\n")


#f_evp_bug_count_monthly.close()        
#f_evp_bug_type.close()
#f_evp_threat_level_monthly.close()
#f_evp_alexa_count.close()
