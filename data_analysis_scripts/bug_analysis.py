import codecs
import libwooyun
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import operator
from operator import itemgetter
from pymongo import Connection

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

f_top_types = open('../data/top_bug_types.txt', 'w')
bugTypeDistPath= '../fig/bug_type_dist.pdf'
bugAttentionPath = "../fig/bug_attention.pdf"
severityAttentionPath = "../fig/severity_attention.pdf"
bugRankPath = "../fig/bug_rank.pdf"
topAttenBugPath = "../data/top_atten_bug.txt"
top_num = 3
topAttenSeverityTh = 30

OWASP_top_2013 = ["SQL Injection", "Authentication Bypass",
                  "XSS", "System/Service Misconfig.",
                  "Sensitive Info. Leakage",
                  "Unauth. Access/Priv. Esc.",
                  "CSRF", "Unpatched System/Service",
                  "URL Redirect"]

markers = ["None", "v", "s"]
linestyles = ['--', '-.', ':']
colors = ['r',"y","g"]

fontSize = 18
figWidth = 7
figHeight = 5

totalBugMonthlyPath = '../fig/total_bug_monthly.pdf'
whMonthlyPath = '../fig/wh_monthly.pdf'
corpMonthlyPath = '../fig/corp_monthly.pdf'
# Warning: This value might need to change if we update
#          the data. It is used for ticks in figures.
month_interval = 3

# Need to see the distribution and manually set this.
cut_off_count = 60

con = Connection()
db = con.wooyun_2
bugs = db.bugs
bug_type_translation = db.bug_type_translation

bug_type_count = {}

bug_type_severity_count = {}

severities = ["高", "中", "低"]

sev_colors = {"高":"r", "中":"yellow", "低":"chartreuse"}

corp_severity_monthly = {}

bug_attention = {}

bug_name_dict = {}

bug_type_dict = {}

bug_corp_dict = {}

serverity_attention = {}
for severity in severities:
    serverity_attention[severity] = {}

for bug in bugs.find().sort([("submit_time",1), ("bug_id",1)]):
    
    bug_type = bug['bug_type']
    bug_id = bug['bug_id']
    attention_num = bug['attention_num']    

    bug_attention[bug_id] = attention_num    
    bug_name_dict[bug_id] = bug['name']
    bug_type_dict[bug_id] = bug_type
    bug_corp_dict[bug_id] = bug['corp']
            
    corp_severity = None    
    if 'corp_threat_level' in bug and bug['corp_threat_level'] in severities:
        corp_severity = bug['corp_threat_level']
    else:
        corp_severity = bug['self_threat_level']
    
    bug_type_name = bug_type.strip()
    translation = bug_type_translation.find_one({'Chinese': bug_type_name})
    if translation != None:
        bug_type_name = translation['English'].strip()
        bug_type_name = libwooyun.mergeBugType(bug_type_name)
        bug_type_name = libwooyun.shortenBugType(bug_type_name)        
        
    bug_type_name = bug_type_name.strip()
    
    if bug_type_name not in bug_type_count:
        bug_type_count[bug_type_name] = 0
        bug_type_severity_count[bug_type_name] = {}
        for severity in severities:
            bug_type_severity_count[bug_type_name][severity] = 0
            
    bug_type_count[bug_type_name] += 1
    bug_type_severity_count[bug_type_name][corp_severity] += 1

    serverity_attention[corp_severity][bug_id] = attention_num

print(sorted(bug_type_count.items(), key=operator.itemgetter(1), reverse=True))

i = 0

bug_type_name_sorted = []
bug_type_count_sorted = []
bug_type_ticks = []

for pair in sorted(bug_type_count.items(), key=operator.itemgetter(1), reverse=True):


    type_name = pair[0]
    
    if type_name == "":
        continue
    
    if i < top_num:
        i += 1
        f_top_types.write(type_name + "," + str(pair[1]) + "\n")

    if pair[1] < cut_off_count:
        break
    
    bug_type_name_sorted.append(type_name)   
    
    if type_name in OWASP_top_2013:
        
        #bug_type_name_sorted.append('*' + pair[0])
        # Tried to use latex's bold, not working        
        
        bug_type_ticks.append(r'\large{\textbf{' + type_name + '}}')
    else:
        bug_type_ticks.append(r'\large{' + type_name + '}')    
    
    bug_type_count_sorted.append(pair[1])

f_top_types.close()



sev_type_sorted = {}

for severity in severities:  
    sev_type_sorted[severity] = []
    for type_name in bug_type_name_sorted:
        sev_type_sorted[severity].append(bug_type_severity_count[type_name][severity])

print(sev_type_sorted)

log_type = True

if log_type:
    
    sev_type_sorted = {}   
    for severity in severities:  
        sev_type_sorted[severity] = []
    
    for type_name in bug_type_name_sorted:
        log_ymax = math.log(bug_type_count[type_name], 10)

        perLow = bug_type_severity_count[type_name]["低"] / bug_type_count[type_name]
        perMed = bug_type_severity_count[type_name]["中"] / bug_type_count[type_name]
        perHig = bug_type_severity_count[type_name]["高"] / bug_type_count[type_name]
        
        sev_type_sorted["低"].append(math.pow(10, log_ymax * perLow))
        sev_type_sorted["中"].append(math.pow(10, log_ymax * (perLow + perMed)) - math.pow(10, log_ymax * perLow))
        sev_type_sorted["高"].append(math.pow(10, log_ymax * (perLow + perMed + perHig)) - math.pow(10, log_ymax * (perLow + perMed)))





# See: http://stackoverflow.com/questions/12920800/mark-tics-in-latex-in-matplotlib
matplotlib.rc('text', usetex = True)


width = 1    # gives histogram aspect to the bar diagram
pos = np.arange(len(bug_type_name_sorted), step = width)

fig_bug_type = plt.figure()

ax = fig_bug_type.add_subplot(111)

#ax.set_xticks(pos - (width / 2))


#ax.set_xticklabels(bug_type_name_sorted)

#ax.set_ylabel('Count', fontsize=fontSize)

# See:
# http://matplotlib.org/examples/pylab_examples/bar_stacked.html
# http://stackoverflow.com/questions/19060144/more-efficient-matplotlib-stacked-bar-chart-how-to-calculate-bottom-values

p1 = plt.bar(pos, sev_type_sorted["低"], width,
       color=sev_colors["低"])  
    
p2 = plt.bar(pos, sev_type_sorted["中"], width,
       color=sev_colors["中"], bottom=sev_type_sorted["低"])  
       
p3 = plt.bar(pos, sev_type_sorted["高"], width,
       color=sev_colors["高"],
       bottom=[sev_type_sorted["低"][j] +sev_type_sorted["中"][j] for j in range(len(bug_type_name_sorted))])  

plt.legend( (p3[0], p2[0], p1[0] ), ('High Severity', 'Medium Severity', 'Low Severity' ) )

if log_type:
    ax.set_yscale('log')
   
# Pie chart is another option
# plt.pie(bug_type_count_sorted, labels=bug_type_name_sorted,
#        autopct='%1.1f%%', shadow=True, startangle=90)

plt.xticks(np.arange(0.5, len(bug_type_name_sorted) + 0.5, width),
           bug_type_ticks, rotation=270)

ax.set_ylabel('Count (log)', fontsize=fontSize)

plt.tick_params(axis='both', which='major', labelsize=14)

#xticks = ax.xaxis.get_major_ticks()

# Potential improvements:
# [*] Put texts on top of the bars
# http://stackoverflow.com/questions/7423445/how-can-i-display-text-over-columns-in-a-bar-chart-in-matplotlib/7423575#7423575
# http://matplotlib.org/examples/api/barchart_demo.html

fig_bug_type.set_size_inches(figWidth, figHeight)

fig_bug_type.tight_layout()

fig_bug_type.savefig(bugTypeDistPath)



# Draw bug-attention graph

bug_sorted = []
attention_sorted = []

max_attention = 0
max_bug = ""

atLeast10attCount = 0

for pair in sorted(bug_attention.items(), key=itemgetter(1), reverse=True):
    bug_sorted.append(pair[0])
    attention_sorted.append(pair[1])
    
    if pair[1] >= 10:
        atLeast10attCount += 1
    
    if pair[1] > max_attention:
        max_attention = pair[1]
        max_bug = pair[0]

print("\nThe max bug " + max_bug + " has " + str(max_attention) + " attentions.")
print("atLeast10attCount = " + str(atLeast10attCount))

fig = plt.figure()

ax = fig.add_subplot(111)

ax.set_xlabel('Vulnerability ranked', fontsize=fontSize)
ax.set_ylabel('Attention Count', fontsize=fontSize)

isLogLog = True

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')


plt.plot(np.arange(len(attention_sorted)), attention_sorted)

fig.tight_layout()

fig.savefig(bugAttentionPath) 

# Draw severity-attention graph

severity_bug_sorted = {}
severity_attention_sorted = {}

topAttenBugFile = codecs.open(topAttenBugPath, "w", "utf-8")

topAttenBugTypeCount = {}
topAttenBugCorpCount = {}

for severity in severities:
    severity_bug_sorted[severity] = []
    severity_attention_sorted[severity] = []
    j = 0
    for pair in sorted(serverity_attention[severity].items(), key=itemgetter(1), reverse=True):
        severity_bug_sorted[severity].append(pair[0])
        severity_attention_sorted[severity].append(pair[1])
        bug_type = bug_type_dict[pair[0]]
        bug_corp = bug_corp_dict[pair[0]]
        if j < topAttenSeverityTh:
            topAttenBugFile.write(pair[0] + ", " + str(pair[1])
                                    + ", " + bug_name_dict[pair[0]]
                                    + ", " + bug_type + "\n")
            if bug_type not in topAttenBugTypeCount:
                topAttenBugTypeCount[bug_type] = 0
            topAttenBugTypeCount[bug_type] += 1 
            
            if bug_corp not in topAttenBugCorpCount:
                topAttenBugCorpCount[bug_corp] = 0
            topAttenBugCorpCount[bug_corp] += 1             
        j+=1

topAttenBugFile.close()

print(topAttenBugTypeCount)
print(topAttenBugCorpCount)

fig = plt.figure()

ax = fig.add_subplot(111)

ax.set_xlabel('Vulnerability ranked', fontsize=fontSize)
ax.set_ylabel('Follower Count', fontsize=fontSize)

isLogLog = True

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')

ptotal = plt.plot(np.arange(1, len(attention_sorted) + 1), attention_sorted)

i = 0
plts = []
for severity in severities:
    p = plt.plot(np.arange(1, len(severity_attention_sorted[severity]) + 1), 
                               severity_attention_sorted[severity], 
                                color=colors[i],
                                linestyle=linestyles[i])
    plts.append(p)    
    i = i + 1

plt.legend( (ptotal[0], plts[0][0], plts[1][0], plts[2][0]), ('Total', 'High', 'Medium', 'Low') )

plt.tick_params(axis='both', which='major', labelsize=14)

fig.tight_layout()

fig.savefig(severityAttentionPath) 