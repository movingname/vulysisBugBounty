import codecs
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import operator
from datetime import datetime
from libwooyun import trendTest, corp_black_list, wh_black_list
from operator import itemgetter
from pymongo import MongoClient
from sklearn import linear_model
from scipy.stats import pearsonr

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

top_corp_size = 6
fontSize = 14

cutoff_reg = 20

cutoff_bug_trend = 50

# We skip corps whose total time length is less than 1 month.
cutoff_day_trend = 120

cutoff_month_trend = "2012-02"

interval_analysis = True

wh_bug_corr_analysis = True

bugArrivalPath = "../fig/bug_arrival.pdf"
corpWhBugPath = "../fig/corp_wh_bug.pdf"
corpBugCountPath = "../fig/corp_bug_count.pdf"

f_top_corps = codecs.open("../data/top_corps.txt", 'w', 'utf-8')

top_corps_translation = {"新浪":"Sina", "搜狐":"Sohu", "百度":"Baidu",
                         "腾讯":"Tencent", "中国电信":"China Telecom", "网易":"163"}

con = MongoClient()
db = con.wooyun_2
bugs = db.bugs
corp_reports = db.corp_reports

corp_bug = {}
corp_wh = {}

    
for bug in bugs.find():

    corp = bug["corp"]
    wh = bug["whitehat"]
    
    if corp in corp_black_list:
        continue

    if wh in wh_black_list:
        continue
  
    if corp not in corp_bug:
        corp_bug[corp] = 0
        corp_wh[corp] = []
    corp_bug[corp] += 1

    if wh not in corp_wh[corp]:
        corp_wh[corp].append(wh)


corp_sorted = []
bug_count_sorted = []

for pair in sorted(corp_bug.items(), key=itemgetter(1), reverse=True):
    corp_sorted.append(pair[0])
    bug_count_sorted.append(pair[1])

 # Get data from HackerOne 

programStatFile = codecs.open("../data/programStat.txt", "r", "utf-8", buffering=0)
progWhCountFile = codecs.open("../data/progWhCount.txt", "r", "utf-8", buffering=0)

progBugCount = {}

for line in programStatFile:

    strs = line.strip().split(",")
    name = strs[0]
    bugCount = int(strs[1])

    progBugCount[name] = bugCount

progWhCount = {}

for line in progWhCountFile:
    strs = line.strip().split(",")
    progWhCount[strs[0]] = int(strs[1])

progSorted = []
progBugCountSorted = []

for pair in sorted(progBugCount.items(), key=itemgetter(1), reverse=True):
    progSorted.append(pair[0])
    progBugCountSorted.append(pair[1])

#######################################
# Draw the wh bug count distribution
#######################################

fig = plt.figure()

ax = fig.add_subplot(111)

ax.set_xlabel('Organizations ranked', fontsize=fontSize)
ax.set_ylabel('Number of Vuln.', fontsize=fontSize)

isLogLog = True

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')


p1 = plt.plot(np.arange(1, len(bug_count_sorted) + 1), bug_count_sorted)
p2 = plt.plot(np.arange(1, len(progBugCountSorted) + 1),
              progBugCountSorted, linestyle="--", color='r')

plt.legend( (p1[0], p2[0]), ('Wooyun', 'HackerOne\_P') )

plt.tick_params(axis='both', which='major', labelsize=14)

fig.tight_layout()

fig.savefig(corpBugCountPath) 


i = 0

top_corps_sorted = []
top_corps_id = {}

trend_corps_sorted = []
trend_corps_id = {}

for pair in sorted(corp_bug.items(), key=operator.itemgetter(1), reverse=True):

    corp = pair[0]
    bug_count = pair[1]

    if i < top_corp_size:
        f_top_corps.write(corp + "," + str(pair[1]) + "\n")
        top_corps_sorted.append(corp)    
        top_corps_id[corp] = i
    
    if bug_count > cutoff_bug_trend:
        trend_corps_sorted.append(corp)
        trend_corps_id[corp] = i
    
    i += 1

f_top_corps.close()


if interval_analysis:
    
    time_intervals_count = []
    time_interval_cutoff = 30
    time_points = []
 
    for i in range(0, len(top_corps_sorted)):
        time_intervals_count.append([])
        for j in range(0, time_interval_cutoff):
            time_intervals_count[i].append(0)
    
    for i in range(0, len(trend_corps_sorted)):
        time_points.append([])
    
    for corp_report in corp_reports.find():
        corp = corp_report['corp']
    
        if (corp not in top_corps_sorted) and (corp not in trend_corps_sorted):
            continue
    
        reports = corp_report['report']    
    
        first = True

        first_time = None
        last_time = None    
    
        for report in sorted(reports, key=lambda k: k['time']) :
        
            report_time = datetime.strptime(report["time"], "%Y-%m-%d %H:%M")

            report_month = report['time'][:7]

            # print(report_time)

            if first:
                first_time = report_time
                last_time = report_time

            diff_time = report_time - last_time
            diff_days = diff_time.days
            last_time = report_time
            elapsed_time = report_time - first_time
            elapsed_days = elapsed_time.days
            
            if corp in trend_corps_sorted and report_month > cutoff_month_trend:
                time_points[trend_corps_id[corp]].append(elapsed_days)               

            if corp in top_corps_sorted:
                if first == False:
                    if diff_days < time_interval_cutoff:
                        time_intervals_count[top_corps_id[corp]][diff_days] += 1
                    else:
                        time_intervals_count[top_corps_id[corp]][time_interval_cutoff - 1] += 1
    
            first = False


    # Do the The Military Handbook Test
    # See: http://www.itl.nist.gov/div898/handbook/apr/section2/apr234.htm#The Military Handbook
    
    skip_list = []    
    
    for corp in trend_corps_sorted:
        if len(time_points[trend_corps_id[corp]]) < cutoff_bug_trend:
            skip_list.append(corp)
        elif time_points[trend_corps_id[corp]][len(time_points[trend_corps_id[corp]]) - 1] - time_points[trend_corps_id[corp]][0] < cutoff_day_trend:
            skip_list.append(corp)
    
    print("Skip the following orgs from trend test: " + str(skip_list) )    
    
    trendTest(trend_corps_sorted, time_points, trend_corps_id, skip_list = skip_list)
    
    # Draw the arrival plots for top organizations

    numRow = 2
    numCol = int(len(top_corps_sorted) / numRow)

    fig, axes = plt.subplots(nrows=numRow, ncols=numCol, 
                             sharex=False, sharey=True)

    fig.set_size_inches(numCol * 2, numRow * 3)


    #for i in range(0, numRow * numCol):
    for i in range(0, numCol):
        for j in range(0, numRow):
            if numRow > 1:
                ax = axes[j][i]
            else:
                ax = axes[i]
            pos = np.arange(1, len(time_intervals_count[i]) + 1)
            ax.set_title(top_corps_translation[top_corps_sorted[i]], fontsize=14)        
            ax.set_yscale('log')
            ax.set_xscale('log')        
            print(time_intervals_count[i])
            ax.plot(pos, time_intervals_count[i], color="b")
   
    fig.tight_layout()

    fig.savefig(bugArrivalPath)       
   
    fig=plt.figure()


if wh_bug_corr_analysis:
    
    corp_wh_count = []
    corp_bug_count = []

    corp_count = 0

    for corp in corp_wh:
        if corp_bug[corp] < cutoff_reg:
            continue
        corp_wh_count.append(len(corp_wh[corp]))
        corp_bug_count.append(corp_bug[corp])
        corp_count += 1
        
    print("corp_count: " + str(corp_count))

    r,p = pearsonr(corp_wh_count, corp_bug_count)
    print("corr = " + str(r) + ", " + str(p))


    regr = linear_model.LinearRegression()

    # See: http://stackoverflow.com/questions/27107057/sklearn-linear-regression-python
    #      http://comments.gmane.org/gmane.comp.python.scikit-learn/6765
    X = np.array(corp_wh_count)[:,np.newaxis]    
    
    regr.fit(X, corp_bug_count)
    
    print('Coefficients: \n' + str(regr.coef_))
    # The mean square error
    print ("Residual sum of squares: %.2f" %
        np.mean((regr.predict(X) - corp_bug_count) ** 2))
    # Explained variance score: 1 is perfect prediction
    print ('Variance score: %.2f' % regr.score(X, corp_bug_count))



    # Regression on HackerOne

    _X1 = []
    Y1 = []
    
    kickOutlier = True

    for prog in progBugCount:
        if progBugCount[prog] < cutoff_reg:
            continue
        
        if kickOutlier:            
            if progBugCount[prog] > 500:
                print("Warning: kicked outliers in correlation study.")
                continue
         
        _X1.append(progWhCount[prog])
        Y1.append(progBugCount[prog])

    r,p = pearsonr(_X1, Y1)
    print("corr = " + str(r) + ", " + str(p))
      
    regr1 = linear_model.LinearRegression()
    X1 = np.array(_X1)[:,np.newaxis]    
    
    regr1.fit(X1, Y1)

    fig, axes = plt.subplots(nrows=1, ncols=2, sharex=False, sharey=False)

    fig.set_size_inches(6, 3.5)

    axes[0].set_xlabel('Wh. count (Wooyun)', fontsize=fontSize)
    axes[0].set_ylabel('Vulnerability count', fontsize=fontSize)
    
    axes[0].xaxis.set_tick_params(labelsize=12)  
    axes[0].yaxis.set_tick_params(labelsize=12)  

    axes[0].scatter(corp_wh_count, corp_bug_count, color='b')
    axes[0].plot(corp_wh_count, regr.predict(X), color='black') 
    axes[0].set_xlim(0, axes[0].get_xlim()[1])
    axes[0].set_ylim(0, 2000)

    axes[0].text(0.1, 0.9, r'$r=0.98$', fontsize = 14, ha='left', va='center', transform=axes[0].transAxes)
    axes[0].text(0.1, 0.8, r'$p=0.00$', fontsize = 14, ha='left', va='center', transform=axes[0].transAxes)
    
    plt.tick_params(axis='both', which='major', labelsize=12)
    
    axes[1].set_xlabel('Wh. count (HackerOne\_P)', fontsize=fontSize)    
    
    axes[1].scatter(_X1, Y1, color='b')
    axes[1].plot(_X1, regr1.predict(X1), color='black') 
    axes[1].set_xlim(0, axes[1].get_xlim()[1])
    axes[1].set_ylim(0, 500) 
    
    
    

    axes[1].text(0.1, 0.9, r'$r=0.95$', fontsize = 14, ha='left', va='center', transform=axes[1].transAxes)
    axes[1].text(0.1, 0.8, r'$p=0.00$', fontsize = 14, ha='left', va='center', transform=axes[1].transAxes)

    fig.tight_layout()

    fig.savefig(corpWhBugPath) 

