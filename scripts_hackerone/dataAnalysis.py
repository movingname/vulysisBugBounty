import time
import codecs
import csv
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import pylab
import operator

from time import mktime
from datetime import datetime
from scipy.stats import chi2, norm, pearsonr
from sklearn import linear_model
import statsmodels.api as sm

# TODO: We currently use file as the database. Should use mongodb instead.

# TODO: We should unify the Wooyun data analysis code and the HackerOne analysis.


matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

doBipartiteAnalysis = True

prefix = "../fig/"

topCorpMonthlyPath = prefix + "topCorpMonthlyH1.pdf"
sameProgTrans = prefix + "sameProgTrans.pdf"
progBugRewardPath = prefix + "progBugReward.pdf"
corrMatrixPath = prefix + "corrMatrix.pdf"

fontSize = 14

allBugsFile = codecs.open("../output/allbugs.txt", "r", "utf-8")

allBountiesFile = codecs.open("../output/allBounties.txt", "r", "utf-8")

monthlyBugFile = codecs.open("monthlyBugH1.txt", "w", "utf-8")

whConFile = codecs.open("whConH1.txt", "w", "utf-8")

whNewActFile = codecs.open("whNewActH1.txt", "w", "utf-8")

IBB = ['Flash', 'Perl', 'PHP', 'Python', 'Apache httpd',
       'Nginx', 'OpenSSL', 'Django', 'Ruby on Rails',
       'Sandbox Escape', 'The Internet', 'Ruby', 'Phabricator',
       'The Internet Bug Bounty']

def fit_powerlaw(data):
    count = 1
    ln_sum = 0
    x_min = 1
    for x in data:
        if x < x_min:
            continue
        count += 1
        
        ln_sum += math.log(x / x_min)

    n = count - 1

    alpha = 1 + n * (1 / ln_sum)
    sigma = (alpha - 1) / math.sqrt(n)
    
    print("alpha = " + str(alpha))
    print("sigma = " + str(sigma))
    
    return (alpha, sigma)


def getShorterTime(timeStr):
    year = timeStr.split("-")[0][2:]
    month = timeStr.split("-")[1]
    return month + "/" + year

def drawTimeline(dataMap, key, ax=None):
    # Take the whole dict as the input will get a list of sorted keys only

    # We skip the last month
    sortedTimeList = sorted(dataMap[key])[:-1]
    bugsMonth = []
    bugsMonthAccu = []
    for i in range(0, len(sortedTimeList)):
        bugsMonth.append(dataMap[key][sortedTimeList[i]])
        bugsMonthAccu.append(dataMap[key][sortedTimeList[i]])
        if i > 0:
            bugsMonthAccu[i] += bugsMonthAccu[i - 1]

    tmp_month_ticks = []
    
    # TODO: automatically determine this
    tmp_month_interval = 6
    
    month_id = 0    
    
    for month in sortedTimeList:
        if month_id % tmp_month_interval == 0 or (month_id == len(sortedTimeList) - 1):
            tmp_month_ticks.append(getShorterTime(month))
        month_id += 1

    # Skip the last month
    timeIDs = range(0, len(dataMap[key]) - 1)

    if ax == None:
        ax = plt.axes()
        # http://stackoverflow.com/questions/10615960/matplotlib-add-strings-as-custom-x-ticks-but-also-keep-existing-numeric-tick
        ax.set_xticklabels(sortedTimeList)

        
        plt.plot(timeIDs, bugsMonth, '-o')

        # See: http://stackoverflow.com/questions/4289891/change-matplotlib-axis-settings
        pylab.ylim(ymin=0)

        plt.suptitle(key + " bug per month.", fontsize=14)

        plt.show()
        
        ax = plt.axes()
        ax.set_xticklabels(sortedTimeList)

        plt.plot(timeIDs, bugsMonthAccu, '-o')


        pylab.ylim(ymin=0)

        plt.suptitle(key + " bug month accu.", fontsize=14)

        plt.show()    

  
    else:

        # We draw a subplot     

        # If ticks are to few, we might need to set this.
        #ax.set_xticks(np.arange(len(sortedTimeList) + 1))
        #print(np.arange(len(sortedTimeList) + 1))

        # This pylab will mess up with the sub figure!
        #pylab.ylim(ymin=0)

        ax.set_ylim([0, max(bugsMonth)])

        ax.set_title(key, fontsize=14)        
        
        ax.plot(timeIDs, bugsMonth, '-')

        ax.set_xticks(np.arange(0, len(sortedTimeList) + 1, tmp_month_interval))
        
        ax.set_xticklabels(tmp_month_ticks)

        plt.tick_params(axis='both', which='major', labelsize=10)



whBugCount = {}
progBugCount = {}

new_wh_monthly = []
active_wh_monthly = []
month_wh = {}

# Bipartite graphs between wh and prog.
# whProgMap[wh][prog] is the number of bugs wh has contributed to prog.
whProgMap = {}
progWhMap = {}


ymStrList = []
ymBugList = []
ymStrToID = {}

#
progBugMonthly = {}
whBugMonthly = {}


# whLastProg[wh] is the last program targeted by the wh
whLastProg = {}

whSameProgCount = {}


progBugTimeList = {}

progRewardList = {}

whNumAccuMonth = {}
progNumAccuMonth = {}
progStartTime = {}


rewardMatched = False


ymID = -1

bugCount = 0

latestTime = None

# NOTICE: We assume that the allBugsFile has already ordered all entries by time.

IBBReportCount = 0

for line in allBugsFile:
    strs = line.split(",;")
 
    progName = strs[1].strip()
    whName = strs[3].strip()
    
    if progName in IBB:
        IBBReportCount += 1
        continue
   
    # See http://www.tutorialspoint.com/python/python_date_time.htm    
    
    evtTime = time.strptime(strs[0], "%Y-%m-%d %H:%M:%S");
    # print(evtTime.tm_mon)
    
    if latestTime == None or latestTime < evtTime:
        latestTime = evtTime
    
    ymStr = strs[0][0:7]
    
    if ymStr not in ymStrList:
        ymStrList.append(ymStr)
        ymBugList.append(0)
        
        new_wh_monthly.append(0)
        active_wh_monthly.append(0)     
        
        month_wh[ymStr] = [] 
        
        if ymID > -1:
            whNumAccuMonth[ymID + 1] = whNumAccuMonth[ymID]
            progNumAccuMonth[ymID + 1] = progNumAccuMonth[ymID]
        else:
            whNumAccuMonth[ymID + 1] = 0
            progNumAccuMonth[ymID + 1] = 0
            
        
        ymID += 1
        ymStrToID[ymStr] = ymID

        
    ymBugList[ymStrToID[ymStr]] += 1
    

    
    bugCount += 1
    
    if progName not in progBugCount:
        progBugCount[progName] = 0
    progBugCount[progName] += 1

    if progName not in progStartTime:
        progStartTime[progName] = ymStrToID[ymStr]
        
        progNumAccuMonth[ymStrToID[ymStr]] += 1
    
    if rewardMatched:
        reward = ""
        
        for i in range(5,len(strs)):
            if strs[i].strip()[0] == '$':
                reward = strs[i].strip()[1:].replace(",","")
                
        if progName not in progRewardList:
            progRewardList[progName] = []
            
        if reward != "":
            progRewardList[progName].append(float(reward))            
        
    if progName not in progWhMap:
        progWhMap[progName] = []
    if whName not in progWhMap[progName]:
        progWhMap[progName].append(whName)
    

    
    if whName not in whBugCount:
        whBugCount[whName] = 0
        new_wh_monthly[ymStrToID[ymStr]] += 1
        whNumAccuMonth[ymStrToID[ymStr]] += 1
    whBugCount[whName] += 1

    if not whName in month_wh[ymStr]:
        month_wh[ymStr].append(whName)
        active_wh_monthly[ymStrToID[ymStr]] += 1


    if whName not in whProgMap:
        whProgMap[whName] = {}

    if whName not in whLastProg:
        whLastProg[whName] = None
    if whName not in whSameProgCount:
        whSameProgCount[whName] = 0
        
    if whLastProg[whName] == progName:
        whSameProgCount[whName] += 1
    
    whLastProg[whName] = progName        
    
    if progName not in whProgMap[whName]:
        whProgMap[whName][progName] = 0
   
    whProgMap[whName][progName] += 1   

    if progName not in progBugMonthly:
        progBugMonthly[progName] = {}    
    
    if ymStr not in progBugMonthly[progName]:
        progBugMonthly[progName][ymStr] = 0
    progBugMonthly[progName][ymStr] += 1    

    if progName not in progBugTimeList:
        progBugTimeList[progName] = []
    progBugTimeList[progName].append(evtTime)

    if whName not in whBugMonthly:
        whBugMonthly[whName] = {}
    
    if ymStr not in whBugMonthly[whName]:
        whBugMonthly[whName][ymStr] = 0
    whBugMonthly[whName][ymStr] += 1   
# print(sorted(whBugCount.items(), key=lambda kv: kv[1], reverse=True))   

print("progNumAccuMonth: " + str(progNumAccuMonth))
print("whNumAccuMonth = " + str(whNumAccuMonth))


# We want to each wh and prog to have a data point in each month
for ymStr in ymStrList:
    for progName in progBugMonthly:
        if ymStr not in progBugMonthly[progName]:
            progBugMonthly[progName][ymStr] = 0
    for whName in whBugMonthly:
        if ymStr not in whBugMonthly[whName]:
            whBugMonthly[whName][ymStr] = 0
    
    # generate a monthly bug count file
    monthlyBugFile.write(ymStr + "," + str(ymBugList[ymStrToID[ymStr]]) + "\n")
    
    whNewActFile.write(ymStr + "," + str(active_wh_monthly[ymStrToID[ymStr]]) + "," + str(new_wh_monthly[ymStrToID[ymStr]]) + "\n" )
    
monthlyBugFile.close()        
whNewActFile.close()

for pair in sorted(whBugCount.items(), key=operator.itemgetter(1), reverse=True):
    whConFile.write(pair[0] + "," + str(pair[1]) + "\n")

whConFile.close()


print("bugCount = " + str(bugCount))
print("IBBReportCount = " + str(IBBReportCount))

print("latestTime = " + str(latestTime))

progSorted = []
progCountSorted = []

for k, v in sorted(progBugCount.items(), key=lambda kv: kv[1], reverse=True):
    progSorted.append(k)
    progCountSorted.append(v)

print("Fit program bug numbers to power law")
fit_powerlaw(progCountSorted)




pos = np.arange(len(progSorted))
width = 1.0     # gives histogram aspect to the bar diagram

ax = plt.axes()
#ax.set_xticks(pos + (width / 2))
#ax.set_xticklabels(list(progSorted))

plt.bar(pos, progCountSorted, width, color='b')
plt.show()





whSorted = []
whCountSorted = []
 
for k, v in sorted(whBugCount.items(), key=lambda kv: kv[1], reverse=True):
    whSorted.append(k)
    whCountSorted.append(v)
    
print("Top wh " + str(whSorted[0]) + " founds " + str(whCountSorted[0]))

print("Fit wh bug numbers to power law")    
fit_powerlaw(whCountSorted)

pos = np.arange(len(whSorted))

ax = plt.axes()
#ax.set_xticks(pos + (width / 2))
#ax.set_xticklabels(list(progSorted))

plt.bar(pos, whCountSorted, width, color='b', edgecolor='b')
plt.show()

ax = plt.axes()
ax.set_yscale('log')
ax.set_xscale('log')
progIDs = range(1, len(progCountSorted) + 1)
plt.scatter(progIDs, progCountSorted)
plt.show()

ax = plt.axes()
ax.set_yscale('log')
ax.set_xscale('log')
whIDs = range(1, len(whCountSorted) + 1)
plt.scatter(whIDs, whCountSorted)
plt.show()


##############################
# We can represent the relation between wh and program
# in a bipartite graph. Then, we can analyze this bipartite
# graph for more information.
##############################

if doBipartiteAnalysis:

    whDegrees = []

    whSum = 0
    whProgSum = 0
    for wh in whProgMap.keys():
        whDegrees.append(len(whProgMap[wh]))
        
        if whBugCount[wh] > 5:
            whSum += 1
            whProgSum += len(whProgMap[wh])
    
    print("Avg orgs per wh = " + str(whProgSum/whSum))

    whDegrees = sorted(whDegrees, reverse=True)
    
    pos = np.arange(len(whDegrees))
    
    plt.bar(pos, whDegrees, width, color='b', edgecolor='b')
    plt.suptitle("Wh degree distribution in wh-prog bipartite.", fontsize=14)
    plt.show()

    ax = plt.axes()
    ax.set_yscale('log')
    ax.set_xscale('log')
    whIDs = range(1, len(whDegrees) + 1)
    plt.scatter(whIDs, whDegrees)
    plt.suptitle("Wh degree distribution in wh-prog bipartite (log-log).", fontsize=14)
    plt.show()


##############################
# Draw total bug monthly
##############################

totalBugMonthly = []

for ymStr in ymStrList:
    count = 0
    for progName in progBugMonthly:
        count += progBugMonthly[progName][ymStr]
    totalBugMonthly.append(count);

ax = plt.axes()
ax.set_xticklabels(ymStrList)

timeIDs = range(1, len(totalBugMonthly) + 1)

plt.plot(timeIDs, totalBugMonthly, '-o')

pylab.ylim(ymin=0)

plt.suptitle("Total monthly bug.", fontsize=14)

plt.show()   



##############################
# Do trend test
##############################

progMostVulMonth = {}


for prog in progBugMonthly:
    progMostVulMonth[prog] = None
    for ymStr in ymStrList:        
        if ymStr in progBugMonthly[prog]:            
            if progMostVulMonth[prog] == None or progBugMonthly[prog][ymStr] > progBugMonthly[prog][progMostVulMonth[prog]]:
                progMostVulMonth[prog] = ymStr
        
print(progMostVulMonth)

progBugElapsedTime = {}

bugCountCutoff = 25

cutoff_days_trend = 30

cutoff_month_trend = "2014-02"

discard_before_spike = False

increaseList = []
decreaseList = []
cantsayList = []

for prog in progSorted:
    
    progBugElapsedTime[prog] = []    
    
    first_time = None

    for _evtTime in progBugTimeList[prog]:
        
        ymStr = time.strftime('%Y-%m-%d %H:%M:%SZ', _evtTime)[0:7]
        
        if discard_before_spike and ymStr <= progMostVulMonth[prog]:
            continue
        
        if ymStr < cutoff_month_trend:
            continue
        
        evtTime = datetime.fromtimestamp(mktime(_evtTime))      
        
        if first_time == None:
            first_time = evtTime
    
        elapsed_time = evtTime - first_time
        elapsed_days = elapsed_time.days
        
        progBugElapsedTime[prog].append(elapsed_days)        
        
        #print(elapsed_days)


    if len(progBugElapsedTime[prog]) < bugCountCutoff:
        continue
    chi_square = 0
    lap_z = 0
    t_end = progBugElapsedTime[prog][len(progBugElapsedTime[prog]) - 1]
    
    #print(progBugElapsedTime[prog])    
    
    #if t_end - progBugElapsedTime[prog][0] < cutoff_days_trend:
    #    print(t_end)
    #    print(progBugElapsedTime[prog][0])
    #    print("Skip1: " + prog)
    #    continue
    
    #if len(progBugElapsedTime[prog]) < bugCountCutoff:
    #    print("Skip2: " + prog)
    #    continue
    
    r = len(progBugElapsedTime[prog]) - 1    
    for tp in progBugElapsedTime[prog]:

        # has to skip the first failure for chi_square.
        if tp == 0:
            continue
        
        chi_square += math.log(t_end / tp)   
        
        lap_z += (tp - t_end / 2)

    chi_square *= 2
    
    lap_z = lap_z * math.sqrt(12 * r) / r / t_end

    test = "Laplace"


    if test == "Chi Square":
        stat = chi_square
        conf90, conf95 = chi2.ppf([0.9, 0.95], 2 * r)
        if stat >= conf95:
            #print(prog + ": decrease with 0.95 conf.")
            decreaseList.append(prog)
        else:
            #print(prog + ": can't say.")  
            cantsayList.append(prog)
    elif test == "Laplace":
        stat = lap_z
        conf5, conf90, conf95 = norm.ppf([0.05, 0.9, 0.95])

        if stat >= conf95:
            #print(prog + ": increase with 0.95 conf.")
            increaseList.append(prog)
        elif stat < conf5:
            #print(prog + ": decrease with 0.95 conf.")
            decreaseList.append(prog)
        else:
            #print(prog + ": can't say.")  
            cantsayList.append(prog)

    #print(prog + " stat = " + str(stat)
    #       + " [0.9, 0.95] = " + [conf90, conf95])

print(str(len(decreaseList)) + " programs have decreasing trends with conf 0.95.")
print(str(len(increaseList)) + " programs have increasing trends with conf 0.95.")
print(str(len(cantsayList)) + " programs cannot be said to have trends.")

print("cantsayList: " + str(cantsayList))

##############################
# Draw monthly bug graphs for top programs.
##############################


numRow = 1
numCol = 3

# See: http://matplotlib.org/examples/pylab_examples/subplots_demo.html
# See: http://stackoverflow.com/questions/1358977/how-to-make-several-plots-on-a-single-page-using-matplotlib
fig, axes = plt.subplots(nrows=numRow, ncols=numCol, sharex=False, sharey=False)

# See: http://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
if numRow == 1:
    fig.set_size_inches(numCol * 2, numRow * 2.5)
else:
    fig.set_size_inches(numRow * 4,numCol * 4)

for i in range(0, numRow * numCol):
    if numRow == 1:
        drawTimeline(progBugMonthly, progSorted[i], axes[i])
    else:
        drawTimeline(progBugMonthly, progSorted[i], axes[int(i / numRow), i % numCol])

print("Time lines for wh.")

fig.tight_layout()

fig.savefig(topCorpMonthlyPath)



fig, axes = plt.subplots(nrows=numRow, ncols=numCol, sharex=False, sharey=False)

if numRow == 1:
    fig.set_size_inches(numCol * 2, numRow * 2.5)
else:
    fig.set_size_inches(numRow * 4,numCol * 4)

for i in range(0, numRow * numCol):
    if numRow == 1:
        drawTimeline(whBugMonthly, whSorted[i], axes[i])
    else:
        drawTimeline(whBugMonthly, whSorted[i], axes[int(i / numRow), i % numCol])
    
# We need this to separate future figures from the last figure
fig=plt.figure()



#################################
# Do a regression of vul number
#################################

# Independent variable 1: total time length

progTotalTimeDays = {}

for prog in progSorted:
    
    first_time = None
    
    total_elapsed_days = 0

    for _evtTime in progBugTimeList[prog]:
        
        ymStr = strs[0][0:7]
        
        evtTime = datetime.fromtimestamp(mktime(_evtTime))      
        
        first_time = evtTime
            
        break    
    
    elapsed_time = datetime.fromtimestamp(mktime(latestTime)) - first_time
    elapsed_days = elapsed_time.days
        
    if elapsed_days > total_elapsed_days:
        total_elapsed_days = elapsed_days
    
    #if total_elapsed_days < 60:
    #    continue
    progTotalTimeDays[prog] = total_elapsed_days

# Independent variable 2: expected monetary reward

# TODO: fill in program info without disclosed info.

progExpReward = {}

progPayNotShow = []

bounties = []

# Include unknown
bountyCount = 0

maxBounty = 0
maxBountyPayer = None

for line in allBountiesFile:

    strs = line.split(",;")
    
    prog = strs[1].strip()
    
    if prog in IBB:
        continue
    
    bountyCount += 1       
    
    if strs[5].strip() == "Unknown":
        if prog not in progPayNotShow:
            progPayNotShow.append(prog)
        continue

    bounty = float(strs[5].strip()[1:].replace(",", ""))
    
    if prog not in progRewardList:
        progRewardList[prog] = []
          
    progRewardList[prog].append(bounty)
    
    bounties.append(bounty)
    
    if bounty > maxBounty:
        maxBounty = bounty
        maxBountyPayer = prog


print("bountyCount = " + str(bountyCount))
print("len(bounties) = " + str(len(bounties)))   
print("max(bounties) = " + str(max(bounties)))
print("max(maxBountyPayer) = " + maxBountyPayer)
print("median(bounties) = " + str(np.median(bounties)))    
print("mean(bounties) = " + str(np.mean(bounties)))

print(np.mean(progRewardList["Yahoo!"]))

print("len(progRewardList) = " + str(len(progRewardList)))

for prog in progRewardList:
    if prog in progPayNotShow:
        progPayNotShow.remove(prog)


progPayCount = 0
progNonPayCount = 0
progNonPayBugCount = 0

for prog in progSorted:
    
    if prog in progPayNotShow:
        progPayCount += 1
        continue
    
    sum_reward = 0
    
    if prog in progRewardList:
        for reward in progRewardList[prog]:
            sum_reward += reward
    if sum_reward == 0:
        progExpReward[prog] = 0
        progNonPayCount += 1
        progNonPayBugCount += progBugCount[prog]
    else:
        progExpReward[prog] = sum_reward / len(progRewardList[prog])
        progPayCount += 1
       #print(prog + " " + str(progExpReward[prog]) + " " + str(len(progRewardList[prog])))

print("len(progExpReward) = " + str(len(progExpReward)))
print("progPayCount = " + str(progPayCount))
print("progNonPayCount = " + str(progNonPayCount))
print("progNonPayBugCount = " + str(progNonPayBugCount))

i = 0
for k, v in sorted(progExpReward.items(), key=lambda kv: kv[1], reverse=True):
    
    #print(k + "," + str(progExpReward[k]) + "," + str(sum(progRewardList[k])))
    
    i += 1
    if i > 2:
        break

# We want to control the amount of reward paid by other 
# programs, as suggested by a CCS reviewer. However, 
# this is not easy due to data issues. For some programs,
# we don't know their payment. Maybe given more data or
# given a good estimation method, we will be able to do this

calcSumExpRewardAccuMonth = False

if calcSumExpRewardAccuMonth:

    sumExpRewardAccuMonth = []

    for ymStr in ymStrList:
        
        ymID = ymStrToID[ymStr]
        
        sumExpRewardAccuMonth.append(0)
        
        if ymID > 0:
            sumExpRewardAccuMonth[ymID] = sumExpRewardAccuMonth[ymID - 1]
        else:
            sumExpRewardAccuMonth[ymID] = 0
    
        for prog in progStartTime:
            if ymID == sumExpRewardAccuMonth[prog]:
                if prog in progExpReward:
                    sumExpRewardAccuMonth[ymID] += progExpReward[prog]
    
    


# Independent variable 3: type of the organization
# Independent variable 4: Alexa rank

first = True

prog_alexa = {}
prog_tags = {}
type_count = {}


reader = csv.reader(open("../input/prog_site_info.csv", "r"))

for row in reader:

    if first:
        first = False
        continue

    prog = row[0]
    alexa = int(row[2])
    org_tags = row[4].split(",")
    
    prog_alexa[prog] = alexa
    prog_tags[prog] = org_tags
    
    for tag in prog_tags[prog]:
        if tag not in type_count:
            type_count[tag] = 0
        type_count[tag] += 1

print(sorted(type_count.items(), key=lambda kv: kv[1], reverse=True))


#prog_reward_policy = {}

#for line in open("reward_policy.txt", "r"):
#    strs = line.strip().split(",")
    
#    progName = strs[0]
#    reward_sum = 0
#    for i in range(1, len(strs)):
#        reward_sum += int(strs[i])
#    prog_reward_policy[progName] = reward_sum / (len(strs) - 1)

    
#for prog in progExpReward:
    
#    if prog in prog_reward_policy:
#        print(prog + ", " + str(prog_reward_policy[prog]) + ", " + str(progExpReward[prog]))
 #       if progExpReward[prog] == 0:
 #           print("WARNING: Use claimed reward for " + prog)
 #           progExpReward[prog] = prog_reward_policy[prog]


#
# Do a correlation matrix
#

numRow = 5
numCol = 5

# See: http://matplotlib.org/examples/pylab_examples/subplots_demo.html
# See: http://stackoverflow.com/questions/1358977/how-to-make-several-plots-on-a-single-page-using-matplotlib
fig, axes = plt.subplots(nrows=numRow, ncols=numCol, sharex=False, sharey=False)

if numRow == 1:
    fig.set_size_inches(numCol * 2, numRow * 2.5)
else:
    fig.set_size_inches(numRow * 3, numCol * 2.5)

var_list = []

var_names = ["Vuln. Count", "Expected Reward", "Alexa Rank (log)", "WH Count", "Time Span"]

num_vars = 5

for i in range(0, num_vars):
    var_list.append([])


stata = open("reg.txt", "w")

for prog in progExpReward:

    if prog not in progBugCount:
        continue

    if prog not in progExpReward:
        continue
    
    if prog not in prog_alexa:
        continue
    
    if prog not in progWhMap:
        continue
    
    if prog not in progTotalTimeDays:
        continue

    var_list[0].append(progBugCount[prog])
    var_list[1].append(progExpReward[prog])
    var_list[2].append(math.log(prog_alexa[prog], 10))
    var_list[3].append(len(progWhMap[prog]))
    var_list[4].append(progTotalTimeDays[prog])
    
    stata.write(str(progBugCount[prog]))
    stata.write("," + str(progExpReward[prog]))
    stata.write("," + str(math.log(prog_alexa[prog], 10)))
    stata.write("," + str(len(progWhMap[prog])))
    stata.write("," + str(progTotalTimeDays[prog]))
    
    ymID = progStartTime[prog]
    
    stata.write("," + str(progNumAccuMonth[ymID]))
    stata.write("," + str(whNumAccuMonth[ymID]))
    stata.write("\n")
    
stata.close()  

for i in range(0, numRow * numCol):
    x = int(i / numRow)
    y = i % numCol
    
    ax = axes[x, y]

    ax.plot(var_list[y], var_list[x], markeredgecolor = 'b', linewidth=0, marker="o")

    ax.set_xlabel(var_names[y])
    ax.set_ylabel(var_names[x])

fig.tight_layout()

fig.savefig(corrMatrixPath)




# We do a regression only using the expected reward

X = []
Y = []

for prog in progExpReward:
    X.append(progExpReward[prog])
    Y.append(progBugCount[prog])


r,p = pearsonr(X, Y)
print("Correlation between expected reward and bug number")
print("r = " + str(r))
print("p = " + str(p))

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

plt.scatter(X, Y, color='b')
plt.plot(X, regr.predict(Xnew), color='black')
 
ax.set_xlim(0, ax.get_xlim()[1])
ax.set_ylim(0, ax.get_ylim()[1])
   
ax.set_xlabel('Expected Reward (USD)', fontsize=18)
ax.set_ylabel('Vulnerability Count', fontsize=18)   

# TODO: need manual assign. Switch to automatic.
ax.text(0.1, 0.9,r'$r = 0.64$', ha='left', va='center', transform=ax.transAxes, fontsize = 18)
ax.text(0.1, 0.8,r'$p-value=1.59e^{-9}$', ha='left', va='center', transform=ax.transAxes, fontsize = 18)


#fig.set_size_inches(figWidth, figHeight + 3)
   
fig.tight_layout()

fig.savefig(progBugRewardPath) 






# Now, let's do the final regression

X = []
Y = []


days = []
peers = []
rewards = []
alexas = []

sample_size = 0

for prog in progSorted:    
    
    # Skip data with missing features    
    
    if prog not in progExpReward:
        print(prog + " not found in progExpReward.")
        continue

    if prog not in progTotalTimeDays:
        print(prog + " not found in progTotalTimeDays.")
        continue

    if prog not in prog_alexa:
        print(prog + " not found in prog_alexa.")
        continue
    
    if prog_alexa[prog] == 99999999:
        continue
    #if prog not in prog_type:
    #    print(prog + " not found in prog_type.")
    #    continue
   
    X.append([])   
   
    X[sample_size].append(progExpReward[prog])
    #X[sample_size].append(math.log(prog_alexa[prog], 10))
    #X[sample_size].append(progTotalTimeDays[prog])
    
    
    weigthedOrgSum = 0
    N = len(progNumAccuMonth) - progStartTime[prog]
    for month in  range(progStartTime[prog], len(progNumAccuMonth)):
        
        if month == progStartTime[prog]:
            weigthedOrgSum += progNumAccuMonth[month] * (len(progNumAccuMonth) - month) / N
        else:
            weigthedOrgSum += (progNumAccuMonth[month] - progNumAccuMonth[month - 1]) * (len(progNumAccuMonth) - month) / N
        
    print(prog + ": " + str(weigthedOrgSum))

    weigthedWhSum = 0
    N = len(whNumAccuMonth) - progStartTime[prog]
    for month in  range(progStartTime[prog], len(whNumAccuMonth)):
        
        if month == progStartTime[prog]:
            weigthedWhSum += whNumAccuMonth[month] * (len(whNumAccuMonth) - month) / N
        else:
            weigthedWhSum += (whNumAccuMonth[month] - whNumAccuMonth[month - 1]) * (len(whNumAccuMonth) - month) / N
    print(prog + ": " + str(weigthedWhSum))    

    
    # Option 1: This is the unweighted vesion
    # weigthedOrgSum = progNumAccuMonth[progStartTime[prog]]
    
    # Option 2: Only consider organizaion peers.
    #X[sample_size].append(weigthedOrgSum)
   
    # Option 3: consider both whs and orgs
    peerComp = weigthedWhSum / weigthedOrgSum
    #X[sample_size].append(peerComp)
    
    Y.append(progBugCount[prog] / progTotalTimeDays[prog] * 30)
    
    # X[sample_size].append(prog_type[prog])    
    
    rewards.append(progExpReward[prog])
    alexas.append(math.log(prog_alexa[prog], 10))
    days.append(progTotalTimeDays[prog])
    peers.append(peerComp)

    sample_size += 1

r,p = pearsonr(days, peers)
print("Correlation between days and # peers")
print("r = " + str(r))
print("p = " + str(p))

r,p = pearsonr(rewards, alexas)
print("Correlation between rewards and alexass")
print("r = " + str(r))
print("p = " + str(p))

r,p = pearsonr(rewards, days)
print("Correlation between rewards and days")
print("r = " + str(r))
print("p = " + str(p))

r,p = pearsonr(alexas, days)
print("Correlation between alexas and days")
print("r = " + str(r))
print("p = " + str(p))

print(prog_alexa)

print("progStartTime: " + str(progStartTime))

print("The sample size for final regression is " + str(sample_size))

#regr = linear_model.LinearRegression()

X = sm.add_constant(X)

Xnew = np.array(X)#[:,np.newaxis]    
Ynew = np.array(Y)

#print(Xnew)

#regr.fit(Xnew, Y)

mod = sm.OLS(Ynew, Xnew)

res = mod.fit()
    
print(res.summary())

#print('Coefficients: \n' + str(regr.coef_))
# The mean square error
#print ("Residual sum of squares: %.2f" %
#    np.mean((regr.predict(Xnew) - Y) ** 2))
# Explained variance score: 1 is perfect prediction
#print ('Variance score: %.2f' % regr.score(Xnew, Y))


###########################
# We now analysis the strategy of white hats
###########################

# We want to know the percentage of same prog transiton for each wh.

whSameProgPercent = {}

whCountTh = 5

for whName in whBugCount:
    if whBugCount[whName] > whCountTh:
        whSameProgPercent[whName] = whSameProgCount[whName] / whBugCount[whName];

#print(whSameProgPercent)
    
    
whNameSorted = []
whPercentSorted = []
 
for k, v in sorted(whSameProgPercent.items(), key=lambda kv: kv[1], reverse=True):
    whNameSorted.append(k)
    whPercentSorted.append(v)

pos = np.arange(len(whSameProgPercent))

ax = plt.axes()
#ax.set_xticks(pos + (width / 2))
#ax.set_xticklabels(list(progSorted))



plt.bar(pos, whPercentSorted, width, color='b', edgecolor='b')
plt.show()

plt.xlabel('Wh (sorted)', fontsize=14)
plt.ylabel('Percentage of same program transition', fontsize=14)

whPercentSortedByCount = []
whPercentSortedByBugCount = []

for whName in whSorted:
    if whBugCount[whName] > whCountTh:
        whPercentSortedByCount.append(whSameProgPercent[whName])
        whPercentSortedByBugCount.append(whBugCount[whName])
        
        # Can select interesting points here
        #if whSameProgPercent[whName] == 0:
        #    print(whName + " finds " + str(whBugCount[whName]) +" with 0 sameProg transition!")

pos = np.arange(len(whSameProgPercent))

ax = plt.axes()
#ax.set_xticks(pos + (width / 2))
#ax.set_xticklabels(list(progSorted))

pylab.xlim(xmin=0)

plt.xlabel('Percentage of same program transition', fontsize=14)
plt.ylabel('Vulnerability Count', fontsize=14)

plt.scatter(whPercentSortedByCount, whPercentSortedByBugCount)
plt.show()


#
# For USENIX 2015
#
fig_wh_time_interval = plt.figure()

ax = fig_wh_time_interval.add_subplot(111)

binwidth = 0.04
xymax = 1
lim = ( int(xymax/binwidth) + 1) * binwidth

bins = np.arange(0, lim + binwidth, binwidth)
ax.hist(whPercentSorted, bins=bins, histtype="step")
ax.set_xlim(0,1)

plt.ylabel('Wh. Count', fontsize=14)

fig_wh_time_interval.set_size_inches(5, 1.5)


fig_wh_time_interval.tight_layout()

fig_wh_time_interval.savefig(sameProgTrans)    


# Generate some files for Wooyun script

programStatFile = codecs.open("../output/programStat.txt", "w", "utf-8", buffering=0)
progWhCountFile = codecs.open("../output/progWhCount.txt", "w", "utf-8", buffering=0)


for prog in progSorted:
    reward = "Unknown"
    if prog in progExpReward:
        reward = "$" + str(progExpReward[prog])
    programStatFile.write(prog + "," + str(progBugCount[prog]) + "," + str(reward) + "\n") 
    progWhCountFile.write(prog + "," + str(len(progWhMap[prog])) + "\n")
    
programStatFile.close()
progWhCountFile.close()