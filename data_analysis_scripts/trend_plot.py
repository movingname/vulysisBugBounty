
import codecs
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from libwooyun import catStatType, stat_type
from pymongo import Connection
import pylab

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

########################################
# The following variables need to be manually specified
########################################

last_month = "2015-07"


totalBugMonthlyPath = '../fig/total_bug_monthly.pdf'
whMonthlyPath = '../fig/wh_monthly.pdf'
corpMonthlyPath = '../fig/corp_monthly.pdf'
bugTypeMonthlyPath = '../fig/bug_type_monthly.pdf'
bugTypeRelativeMonthlyPath = '../fig/bug_type_relative_monthly.pdf'
corpSeverityMonthlyPath = '../fig/corp_severity_monthly.pdf'
corpSeverityRelativeMonthlyPath = '../fig/corp_severity_relative_monthly.pdf'
topCorpMonthlyPath = '../fig/top_corp_monthly.pdf'
statMonthlyPath = '../fig/stat_monthly.pdf'

f_top_types = open('../data/top_bug_types.txt', 'r')
f_top_corp = codecs.open("../data/top_corps.txt", 'r', 'utf-8')


# Obtained from HackerOne scripts
monthlyBugFile = codecs.open("../data/monthlyBugH1.txt", "r", "utf-8")
whNewActFile = codecs.open("../data/whNewActH1.txt", "r", "utf-8")

# Warning: This value might need to change if we update
#          the data. It is used for ticks in figures.
month_interval = 3

marker_freq = 3

con = Connection()
db = con.wooyun_2
bugs = db.bugs
bug_type_translation = db.bug_type_translation

fontSize = 18

#markers = ["None", "v", "s", "D", "*", "h", "|", "p", "o", "8", "+"]

markers = ["None", "None", "None", "v", "*", "h", "|", "p", "o", "8", "+"]

colors = ('y', 'b', 'r', 'g', 'y', 'm', 'k')

linestyles = ['-', '-', '--', '-', '--', '--', '-']
#linestyles = ['-', '-', '-', '-']



month_list = []

month_id_map = {}

total_bug_monthly = []

new_wh_monthly = []
active_wh_monthly = []
month_wh = {}
wh_list = []


new_corp_monthly = []
targeted_corp_monthly = []
month_corp = {}
corp_list = []


top_bug_types = []
bug_type_monthly = {}

for line in f_top_types:
    top_bug_types.append(line.split(',')[0])
    bug_type_monthly[line.split(',')[0]] = []


severities = ["高", "中", "低"]

severity_translation = {"低":"Low Severity", "中":"Medium Severity", "高":"High Severity"}

corp_severity_monthly = {}
for severity in severities:
    corp_severity_monthly[severity] = []

top_corps = []
top_corps_monthly = {}

for line in f_top_corp:
    top_corps.append(line.split(',')[0])
    top_corps_monthly[line.split(',')[0]] = []

top_corps_translation = {"新浪":"Sina", "搜狐":"Sohu", "百度":"Baidu",
                         "腾讯":"Tencent", "中国电信":"China Telecom",
                         "中国移动":"China Mobile", "网易":"163",
                         "中国联通":"China Unicom"}


# Stores the id of the month that splits the corp's timeline
# into 2 halves
corp_half_month = {}
corp_1_half_bug = {}
corp_2_half_bug = {}

# When the number of months is odd, we need to split
# that month into two halves also.
corp_half_switch = True

corp_bug = {}


# Should do corp_response_analysis.py before plotting
# the trend of response behavior.
stat_monthly = {}

for stat in stat_type:
    stat_monthly[stat] = []



corp_severity_count = 0

month_id = 0

first_month = ""

def get_month_id(first_month, month):
    first_year = int(first_month.split("-")[0])
    first_mon = int(first_month.split("-")[1])
    year = int(month.split("-")[0])
    mon = int(month.split("-")[1])
    return (year - first_year) * 12 + mon - first_mon

# def get_month_string(first_month, month_id):

totalBug = 0

for bug in bugs.find().sort([("submit_time",1), ("bug_id",1)]):

    id_year = int(bug['bug_id'][7:11])
    id_count = int(bug['bug_id'][12:])

    submit_month = bug['submit_time'][:7]
    
    whitehat = bug['whitehat']
    
    corp = bug['corp']
    
    bug_type = bug['bug_type']
    
    stat = catStatType(bug["status"])
    
    corp_severity = None    
    if 'corp_threat_level' in bug and bug['corp_threat_level'] in severities:
        corp_severity = bug['corp_threat_level']
        corp_severity_count += 1
    else:
        corp_severity = bug['self_threat_level']

    if submit_month > last_month:
        continue
    
    if first_month == "":
        first_month = submit_month
  
    if not submit_month in month_list:       
        
        assert month_id == get_month_id(first_month, submit_month)        
        
        month_list.append(submit_month)
        
        total_bug_monthly.append(0)
        new_wh_monthly.append(0)
        active_wh_monthly.append(0)

        new_corp_monthly.append(0)
        targeted_corp_monthly.append(0) 

        for severity in severities:
            corp_severity_monthly[severity].append(0)
            
        for stat in stat_type:
            stat_monthly[stat].append(0)       
       
        month_id_map[submit_month] = month_id        
        month_wh[submit_month] = []        
        month_corp[submit_month] = []
 
        for top_type in top_bug_types:
            bug_type_monthly[top_type].append(0)
 
        for top_corp in top_corps:
            top_corps_monthly[top_corp].append(0)
       
        month_id += 1
    
    submit_month_id = month_id_map[submit_month]    
    
    if corp not in corp_half_month:
       last_id = get_month_id(first_month, last_month)
       corp_half_month[corp] = (last_id - submit_month_id) / 2 + submit_month_id
       corp_1_half_bug[corp] = 0
       corp_2_half_bug[corp] = 0
       corp_bug[corp] = 0
      
    corp_bug[corp] += 1
    
    if submit_month_id < corp_half_month[corp]:
        corp_1_half_bug[corp] += 1
    elif submit_month_id > corp_half_month[corp]:
        corp_2_half_bug[corp] += 1
    else:
        if corp_half_switch:
            corp_1_half_bug[corp] += 1
        else:
            corp_2_half_bug[corp] += 1
        corp_half_switch = not corp_half_switch
    
    stat_monthly[stat][submit_month_id] += 1    
    
    if not whitehat in wh_list:    
        wh_list.append(whitehat)
        new_wh_monthly[submit_month_id] += 1
        
    if not whitehat in month_wh[submit_month]:
        month_wh[submit_month].append(whitehat)
        active_wh_monthly[submit_month_id] += 1

    if not corp in corp_list:    
        corp_list.append(corp)
        new_corp_monthly[submit_month_id] += 1
        
    if not corp in month_corp[submit_month]:
        month_corp[submit_month].append(corp)
        targeted_corp_monthly[submit_month_id] += 1
    
    total_bug_monthly[submit_month_id] += 1
    
    bug_type_name = bug_type.strip()
    translation = bug_type_translation.find_one({'Chinese': bug_type_name})
    if translation != None:
        bug_type_name = translation['English'].strip()
    bug_type_name = bug_type_name.strip()    
    
    if bug_type_name in top_bug_types:
        bug_type_monthly[bug_type_name][submit_month_id] += 1

    if corp in top_corps:
        top_corps_monthly[corp][submit_month_id] += 1

    if corp_severity != None:
        corp_severity_monthly[corp_severity][submit_month_id] += 1

    totalBug += 1
    
print("totalBug: " + str(totalBug) )
print("len(wh_list)" + str(len(wh_list)))
print("len(corp_list)" + str(len(corp_list)))

month_ticks = []

month_id = 0
last_year = None

for month in month_list:
    if month_id % month_interval == 0 or (month_id == len(month_list) - 1):
        month_ticks.append(month)
    month_id += 1
    

print("Total months: " + str(len(month_list)))

print("corp_severity_count: " + str(corp_severity_count))



last_month_id = get_month_id(first_month, last_month)

increase_count = 0
decrease_count = 0
average_increase = 0
average_decrease = 0

for corp in corp_list:
    
    if corp_bug[corp] > 10 and last_month_id - corp_half_month[corp] >= 6:
        change = (corp_2_half_bug[corp] - corp_1_half_bug[corp]) / corp_1_half_bug[corp]        
        if change < 0:
            decrease_count += 1
            average_decrease += change
        else:
            increase_count += 1
            average_increase += change

print("decrease_count = " + str(decrease_count))
print("increase_count = " + str(increase_count))

average_decrease /= decrease_count
average_increase /= increase_count

print("average_decrease = " + str(average_decrease))
print("average_increase = " + str(average_increase))


h1_total_bug = {}

for line in monthlyBugFile:
    month = line.strip().split(",")[0]
    count = int(line.strip().split(",")[1])
    h1_total_bug[month] = count
    
h1_total_monthly = []    
    
for month in month_list:
    if month not in h1_total_bug:
        h1_total_monthly.append(0)
    else:
        h1_total_monthly.append(h1_total_bug[month])


timeIDs = range(0, len(month_list))

fig_total_bug= plt.figure()

ax = fig_total_bug.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

ax.plot(timeIDs, total_bug_monthly, marker=markers[0], markevery=marker_freq,
        label="Wooyun", color=colors[1], linestyle=linestyles[1])
ax.plot(timeIDs, h1_total_monthly, marker=markers[0], markevery=marker_freq,
        label="HackerOne\_P", color=colors[2], linestyle=linestyles[2])


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)

ax.legend(loc=2)

ax.set_xlim(0, len(month_list) - 1)

plt.tick_params(axis='both', which='major', labelsize=12)

fig_total_bug.tight_layout()

fig_total_bug.savefig(totalBugMonthlyPath)



_new_wh_monthly_h1 = {}
_active_wh_monthly_h1 = {}

for line in whNewActFile:
    month = line.strip().split(",")[0]
    _active_wh_monthly_h1[month] = int(line.strip().split(",")[1])
    _new_wh_monthly_h1[month] = int(line.strip().split(",")[2])

new_wh_monthly_h1 = []
active_wh_monthly_h1 = []

for month in month_list:
    if month not in h1_total_bug:
        new_wh_monthly_h1.append(0)
        active_wh_monthly_h1.append(0)
    else:
        new_wh_monthly_h1.append(_new_wh_monthly_h1[month])
        active_wh_monthly_h1.append(_active_wh_monthly_h1[month])


fig_wh= plt.figure()

ax = fig_wh.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

ax.plot(timeIDs, active_wh_monthly, marker=markers[0], markevery=marker_freq,
        label="Active (Wooyun)", color=colors[1], linestyle=linestyles[1])
ax.plot(timeIDs, new_wh_monthly, marker=markers[0], markevery=marker_freq,
        label="New (Wooyun)", color=colors[2], linestyle=linestyles[2])
ax.plot(timeIDs, active_wh_monthly_h1, marker=markers[3], markevery=marker_freq,
        label="Active (HackerOne\_P)", color=colors[3], linestyle=linestyles[3])
ax.plot(timeIDs, new_wh_monthly_h1, marker=markers[3], markevery=marker_freq,
        label="New (HackerOne\_P)", color=colors[4], linestyle=linestyles[4])

plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)

ax.set_xlim(0, len(month_list) - 1)

plt.tick_params(axis='both', which='major', labelsize=12)

fig_wh.tight_layout()

fig_wh.savefig(whMonthlyPath)





fig_corp= plt.figure()

ax = fig_corp.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

ax.plot(timeIDs, targeted_corp_monthly, marker=markers[0],
        label="Total Org.", color=colors[1], linestyle=linestyles[1])
ax.plot(timeIDs, new_corp_monthly, marker=markers[0],
        label="New Org.", color=colors[2], linestyle=linestyles[2])


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)

ax.set_xlim(0, len(month_list) - 1)

plt.tick_params(axis='both', which='major', labelsize=12)

fig_corp.tight_layout()

fig_corp.savefig(corpMonthlyPath)


# Draw the trend of top vulnerability types (absolute)

fig_bug_type= plt.figure()

ax = fig_bug_type.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

i = 1

for top_type in top_bug_types:
    ax.plot(timeIDs, bug_type_monthly[top_type], marker=markers[i],
            label=top_type, color=colors[i], linestyle=linestyles[i],
            markevery = marker_freq)
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

ax.set_xlim(0, len(month_list) - 1)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)

plt.tick_params(axis='both', which='major', labelsize=12)

fig_bug_type.tight_layout()

fig_bug_type.savefig(bugTypeMonthlyPath)


######################################################
# Draw the trend of top vulnerability types (relative)
######################################################

fig= plt.figure()

ax = fig.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

i = 1

for top_type in top_bug_types:
    
    relative_monthly = []
    for j in range(0, len(bug_type_monthly[top_type])):
        relative_monthly.append(bug_type_monthly[top_type][j] / total_bug_monthly[j])
    
    ax.plot(timeIDs, relative_monthly, marker=markers[i], markevery = marker_freq,
            label=top_type, color=colors[i], linestyle=linestyles[i])
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

ax.set_xlim(0, len(month_list) - 1)

plt.tick_params(axis='both', which='major', labelsize=12)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Percentage', fontsize=fontSize)
ax.legend(loc=1)


fig.tight_layout()

fig.savefig(bugTypeRelativeMonthlyPath)







fig_top_corp_monthly = plt.figure()

ax = fig_top_corp_monthly.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

i = 1

for top_corp in top_corps:
    ax.plot(timeIDs, top_corps_monthly[top_corp], marker=markers[i],
            label=top_corps_translation[top_corp], color=colors[i],
            linestyle=linestyles[i], markevery=marker_freq)
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

ax.set_xlim(0, len(month_list) - 1)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)


fig_top_corp_monthly.tight_layout()

fig_top_corp_monthly.savefig(topCorpMonthlyPath)



######################################################
# Draw the trend of different severities (absolute)
######################################################


fig_corp_severity= plt.figure()

ax = fig_corp_severity.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

i = 1

for severity in severities:
    ax.plot(timeIDs, corp_severity_monthly[severity], marker=markers[i],
            label=severity_translation[severity], color=colors[i], 
            linestyle=linestyles[i], markevery=marker_freq)
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)

ax.set_xlim(0, len(month_list) - 1)

plt.tick_params(axis='both', which='major', labelsize=12)

fig_corp_severity.tight_layout()

fig_corp_severity.savefig(corpSeverityMonthlyPath)


######################################################
# Draw the trend of different severities (relative)
######################################################

fig = plt.figure()

ax = fig.add_subplot(111)

plt.xticks(rotation=290)

#pylab.yticks(fontsize=14)
#pylab.xticks(fontsize=10)

i = 1

for severity in severities:
    
    relative_monthly = []
    for j in range(0, len(corp_severity_monthly[severity])):
        relative_monthly.append(corp_severity_monthly[severity][j] / total_bug_monthly[j])
    
    ax.plot(timeIDs, relative_monthly, marker=markers[i],
            label=severity_translation[severity], color=colors[i], 
            linestyle=linestyles[i], markevery=marker_freq)
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Percentage', fontsize=fontSize)
ax.legend(loc=1)

plt.tick_params(axis='both', which='major', labelsize=12)

ax.set_xlim(0, len(month_list) - 1)

fig.tight_layout()

fig.savefig(corpSeverityRelativeMonthlyPath)








#
# Draw stat monthly
#

fig = plt.figure()

plt.xticks(rotation=290)

ax = fig.add_subplot(111)

i = 1

for stat in stat_type:
    if stat == "Other":
        continue
    ax.plot(timeIDs, stat_monthly[stat], marker=markers[i],
            label=stat, color=colors[i], markevery=marker_freq,
            linestyle=linestyles[i])
    i += 1


plt.xticks(np.arange(0, len(month_list) + 1, month_interval))

ax.set_xticklabels(month_ticks)

#axCost.set_xlabel('', fontsize=fontSize)
ax.set_ylabel('Count', fontsize=fontSize)
ax.legend(loc=2)

ax.set_xlim(0, len(month_list) - 1)

fig.tight_layout()

fig.savefig(statMonthlyPath)



def getShorterTime(timeStr):
    year = timeStr.split("-")[0][2:]
    month = timeStr.split("-")[1]
    return month + "/" + year


numRow = 1
numCol = 3


tmp_month_ticks = []

month_id = 0
last_year = None

tmp_month_interval = 16

for month in month_list:
    if month_id % tmp_month_interval == 0 or (month_id == len(month_list) - 1):
        tmp_month_ticks.append(getShorterTime(month))
    month_id += 1

fig, axes = plt.subplots(nrows=numRow, ncols=numCol, sharex=False, sharey=False)

fig.set_size_inches(numCol * 2, numRow * 2.5)

for i in range(0, numRow * numCol):
    if numRow == 1:
        ax = axes[i]
    else:
        ax = axes[int(i / numCol), i % (numRow + 1)]
        # See: http://stackoverflow.com/questions/19626530/python-xticks-in-subplots
    ax.set_title(top_corps_translation[top_corps[i]])              
    ax.plot(timeIDs, top_corps_monthly[top_corps[i]], color="b")
    ax.set_xlim(0, len(month_list) - 1)
    ax.set_xticks(np.arange(0, len(month_list) + 1, 16))
    ax.set_xticklabels(tmp_month_ticks)
    #pylab.rcParams['xtick.major.pad']='10'
      
    plt.tick_params(axis='both', which='major', labelsize=10)

fig.tight_layout()

fig.savefig(topCorpMonthlyPath)

fig=plt.figure()
