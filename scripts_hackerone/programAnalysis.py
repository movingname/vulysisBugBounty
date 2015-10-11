import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import codecs
import time
import operator
from matplotlib.ticker import FuncFormatter
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pylab
from sklearn import datasets, linear_model
from scipy.stats import pearsonr

cutoff_bug_count = 20

fontSize = 18

regressionAnalysis = True

progDistPath= 'prog_dist.pdf'
progWhBugPath = 'prog_wh_bug_scatter.pdf'

programStatFile = codecs.open("programStat.txt", "r", "utf-8", buffering=0)
progWhCountFile = codecs.open("progWhCount.txt", "r", "utf-8", buffering=0)


progBugCount = {}
progMinBounty = {}

totalProgCount = 0
bountyProgs = []
aboveCutoffTotalProgCount = 0
aboveCutoffBountyProgCount = 0

totalBugCount = 0
bountyBugCount = 0

for line in programStatFile:
    
    strs = line.strip().split(",")
    name = strs[0]
    bugCount = int(strs[1])
    
    progBugCount[name] = bugCount
    progMinBounty[name] = 0
    if strs[2] != "None":
        progMinBounty[name] = int(strs[2][1:].strip())
        bountyProgs.append(name)
        bountyBugCount += bugCount
        
    if bugCount > cutoff_bug_count:
        aboveCutoffTotalProgCount += 1
        if strs[2] != "None":
            aboveCutoffBountyProgCount += 1
    
    totalProgCount += 1
    totalBugCount += bugCount
    
print("totalProgCount: " + str(totalProgCount))
print("bountyProgCount: " + str(len(bountyProgs)))
print("aboveCutoffTotalProgCount: " + str(aboveCutoffTotalProgCount))
print("aboveCutoffBountyProgCount: " + str(aboveCutoffBountyProgCount))
print("totalBugCount: " + str(totalBugCount))
print("bountyBugCount: " + str(bountyBugCount))

progWhCount = {}

totalWhCount = 0

for line in progWhCountFile:
    strs = line.strip().split(",")
    progWhCount[strs[0]] = int(strs[1])
    totalWhCount += int(strs[1])

print("totalWhCount: " + str(totalWhCount))

progNameSorted = []
progCountSorted = []

for pair in sorted(progBugCount.items(), key=operator.itemgetter(1), reverse=True):
    name = pair[0]    
    bugCount = pair[1]
    if bugCount < cutoff_bug_count:
        continue
    print(pair)
    progCountSorted.append(bugCount)
    if name in bountyProgs:
        progNameSorted.append(r'\textbf{' + name + '}')
    else:
        progNameSorted.append(name)


# See: http://stackoverflow.com/questions/12920800/mark-tics-in-latex-in-matplotlib
matplotlib.rc('text', usetex = True)

pos = np.arange(0, len(progNameSorted) + 1)
width = 1     # gives histogram aspect to the bar diagram

fig_bug_type = plt.figure()

ax = fig_bug_type.add_subplot(111)

#ax.set_xticks(pos - (width / 2))

#ax.set_xticklabels(bug_type_name_sorted)

ax.set_ylabel('Count', fontsize=fontSize)

progCountSorted.insert(0, max(progCountSorted))

plt.step(pos, progCountSorted, color="b")

progCountSorted.remove(max(progCountSorted))

# Pie chart is another option
# plt.pie(bug_type_count_sorted, labels=bug_type_name_sorted,
#        autopct='%1.1f%%', shadow=True, startangle=90)

plt.xticks(np.arange(0, len(progNameSorted), 1),
           progNameSorted, rotation=270)

#xticks = ax.xaxis.get_major_ticks()

# Potential improvements:
# [*] Put texts on top of the bars
# http://stackoverflow.com/questions/7423445/how-can-i-display-text-over-columns-in-a-bar-chart-in-matplotlib/7423575#7423575
# http://matplotlib.org/examples/api/barchart_demo.html

#fig_bug_type.set_size_inches(figWidth, figHeight + 3)

fig_bug_type.tight_layout()

fig_bug_type.savefig(progDistPath)    
   

if regressionAnalysis:
    
    X = []
    Y = []

    for prog in progBugCount:
        if progBugCount[prog] < cutoff_bug_count:
            continue
        X.append(progWhCount[prog])
        Y.append(progBugCount[prog])

    print("Prog Count: " + str(len(X)))
    r,p = pearsonr(X, Y)
    print("corr = " + str(r) + ", " + str(p))


    regr = linear_model.LinearRegression()

    # See: http://stackoverflow.com/questions/27107057/sklearn-linear-regression-python
    #      http://comments.gmane.org/gmane.comp.python.scikit-learn/6765
    Xnew = np.array(X)[:,np.newaxis]    
    
    regr.fit(Xnew, Y)
    
    print('Coefficients: \n' + str(regr.coef_))
    # The mean square error
    print ("Residual sum of squares: %.2f" %
        np.mean((regr.predict(Xnew) - Y) ** 2))
    # Explained variance score: 1 is perfect prediction
    print ('Variance score: %.2f' % regr.score(Xnew, Y))

    fig = plt.figure()

    ax = fig.add_subplot(111)

    ax.set_xlabel('white hat count', fontsize=fontSize)
    ax.set_ylabel('vulnerability count', fontsize=fontSize)

    plt.scatter(X, Y, color='b')
    plt.plot(X, regr.predict(Xnew), color='black')
 
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_ylim(0, ax.get_ylim()[1])
   
    fig.set_size_inches(figWidth, figHeight + 3)
   
    fig.tight_layout()

    fig.savefig(progWhBugPath) 




