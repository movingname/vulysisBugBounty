####################################
#
# This script analyzes temporal patterns of white hats' submission records
# that we call strategy. Follwoing functionalities are implemented:
#   - Calculate (same_site_percentage, same_type_percentage) for each white hat
#   - Calculate the distribution of vulnerability submission time intervals
#
# To run this script, you should start IDLE using:
# python -m idlelib.idle
# See more at:
# http://stackoverflow.com/questions/17139658/how-do-i-resolve-nonetype-object-has-no-attribute-write-error-with-scikit-le
#
####################################

import codecs   #Need this to handle Chinese characters  
import libwooyun 
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from matplotlib.ticker import NullFormatter
from operator import itemgetter
from pymongo import Connection

matplotlib.rcParams['ps.useafm'] = True
matplotlib.rcParams['pdf.use14corefonts'] = True
matplotlib.rcParams['text.usetex'] = True

con = Connection()
db = con.wooyun_2
whitehat_reports = db.whitehat_reports
corp_alexa = db.corp_alexa

fontSize = 14

data_folder = "../data/"
intervalDistPath = "../fig/wh_time_interval_dist.pdf"
transitionScatterPath = "../fig/transition_scatter.pdf"
transitionScatterAugPath = "../fig/transition_scatter_aug.pdf"
whitehat_strategy = codecs.open(data_folder + 'whitehat_strategy.csv', 'w', 'utf-8')
time_intervals = codecs.open(data_folder + 'time_intervals.csv', 'w', 'utf-8')

wh_regression_file = open(data_folder + 'wh_regression.txt', "w")
monthly_low_alexa_dict = {}

month_list = []

time_intervals_count = []
time_interval_cutoff = 1320
for i in range(0, time_interval_cutoff):
    time_intervals_count.append(0)

Alexa_not_found_count = 0
Alexa_found_count = 0

all_site = set()
all_type = set()

same_sites = []
same_types = []

wh_bug_count = {}
wh_same_site = {}
wh_same_type = {}

wh_site_dict = {}
wh_type_dict = {}

wh_age = {}

bug_count_cut_off = 5

num_points_in_trans = 0

whitehat_strategy.write("whitehat,same_corp,same_type,total\n")

for whitehat_report in whitehat_reports.find():
    
    whitehat = whitehat_report['whitehat']
    reports = whitehat_report['report']

    if whitehat in libwooyun.wh_black_list:
        continue

    wh_site_dict[whitehat] = {}
    wh_type_dict[whitehat] = {}

    last_bug_type = ""
    last_corp = ""
    type_1 = 0 # same site
    type_2 = 0 # same type
    trans_count = 0
    first = True

    first_time = None
    last_time = None
    
    high_alexa_counts = []
    low_alexa_counts = []
    times = []
    high_alexa_counts.append(0)
    low_alexa_counts.append(0)
    times.append(0)
    last_diff_months = 0

    high_alexa_count = 0
    low_alexa_count = 0

    monthly_low_alexa_wh = {}
    
    for report in sorted(reports, key=lambda k: k['time']) :

        corp = report['corp']
        bug_type = report['bug_type']
        
        if corp not in all_site:
            all_site.add(corp)
        
        if bug_type not in all_type:
            all_type.add(bug_type)

        if corp not in wh_site_dict[whitehat]:
            wh_site_dict[whitehat][corp] = 0
        wh_site_dict[whitehat][corp] += 1

        if bug_type not in wh_type_dict[whitehat]:
            wh_type_dict[whitehat][bug_type] = 0
        wh_type_dict[whitehat][bug_type] += 1

        month = report["time"][0:7]
        
        if not month in month_list:
            month_list.append(month)
            monthly_low_alexa_dict[month] = []


        report_time = datetime.strptime(report["time"], "%Y-%m-%d %H:%M")

        if first:
            first_time = report_time
            last_time = report_time
		
	# For strategy analysis
		
        #Use this to verify whether reports are in the correct time order
        #if report["time"] < cur_time:
        #    print("time error!")
        #else:
        #    cur_time = report["time"]

            
        diff_time = report_time - last_time
        diff_days = diff_time.days
        last_time = report_time

        if first == False:
            if diff_days < time_interval_cutoff:
                time_intervals_count[diff_days] = time_intervals_count[diff_days] + 1
            else:
                time_intervals_count[time_interval_cutoff - 1] = time_intervals_count[time_interval_cutoff - 1] + 1

            if last_bug_type == bug_type:
                type_2 = type_2 + 1
                
            if last_corp == corp:
                type_1 = type_1 + 1

            trans_count = trans_count + 1
            
            last_bug_type = bug_type
            last_corp = corp
		
        # For trend analysis
        passed_time = report_time - first_time

        # We can not directly get diff months, so we have to do this
        diff_months = int(passed_time.days / 30)	
        if diff_months != last_diff_months:
            for i in range(last_diff_months + 1, diff_months + 1):
                high_alexa_counts.append(0)
                low_alexa_counts.append(0)
                times.append(i)
        last_diff_months = diff_months

        corp_alexa_pair = corp_alexa.find_one({'corp': corp})

        if corp_alexa_pair != None and corp_alexa_pair['alexa'] != None:
            alexa = corp_alexa_pair['alexa']

            if alexa < 100:
                high_alexa_counts[diff_months] = high_alexa_counts[diff_months]+ 1    
                high_alexa_count = high_alexa_count + 1
            elif alexa >= 1000:
                low_alexa_counts[diff_months] = low_alexa_counts[diff_months] + 1
                low_alexa_count = low_alexa_count + 1
                if not month in monthly_low_alexa_wh:
                    monthly_low_alexa_wh[month] = 0
                monthly_low_alexa_wh[month] = monthly_low_alexa_wh[month] + 1
            Alexa_found_count = Alexa_found_count + 1
        else:
            Alexa_not_found_count = Alexa_not_found_count + 1

        first = False

    for month in monthly_low_alexa_wh:
        monthly_low_alexa_dict[month].append(monthly_low_alexa_wh[month])

    total_time = last_time - first_time
    
    wh_age[whitehat] = total_time.days    
    
    #if high_alexa_count >= 10:
        #corr = spearmanr(high_alexa_counts, times)
        #print("High Alexa Trend: " + whitehat + " corr = " + str(corr[0]) + ", p = " + str(corr[1]))
        #plt.plot(times, high_alexa_counts , 'ro')
        #plt.show()
        #print(high_alexa_counts)
        #print(times)
        #input("Press Enter to continue...")

    #if low_alexa_count >= 10:
        #corr = spearmanr(low_alexa_counts, times)
        #print("Low Alexa Trend: " + whitehat + " corr = " + str(corr[0]) + ", p = " + str(corr[1]))
        
    if trans_count > bug_count_cut_off - 1:
        whitehat_strategy.write(whitehat + "," + str(type_1 / trans_count) + "," + str(type_2 / trans_count) + "," + str(trans_count) + "\n")
        same_sites.append(type_1 / trans_count)
        same_types.append(type_2 / trans_count)
        num_points_in_trans += 1
        
        wh_bug_count[whitehat] = trans_count + 1
        wh_same_site[whitehat] = type_1 / trans_count  
        wh_same_type[whitehat] = type_2 / trans_count
        
        wh_regression_file.write(str(wh_bug_count[whitehat]) + ", "
                                + str(len(wh_type_dict[whitehat])) + ", "
                                + str(len(wh_site_dict[whitehat])) + ", "
                                + str(wh_age[whitehat]) + "\n")

wh_regression_file.close()

print("Alexa not found count: " + str(Alexa_not_found_count));
print("Alexa found count: " + str(Alexa_found_count));

print("num_points_in_strategy: " + str(num_points_in_trans))

print("consecutive submission number: " + str(sum(time_intervals_count)))

#print(time_intervals_count)

whitehat_strategy.close()

site_shannon = []
type_shannon = []
site_shannon_cat = {}
type_shannon_cat = {}

site_simpson = []
type_simpson = []
site_simpson_cat = {}
type_simpson_cat = {}

site_count = []
type_count = []
site_count_cat = {}
type_count_cat = {}

# Here, we categorize white hats into three sets with different
# number of vulnerability discoveries. Then we can overlay it 
# on the scatter plot.

categories = {"h", "m", "l"}
same_site_cat = {}
same_type_cat = {}

for cat in categories:
    same_site_cat[cat] = []
    same_type_cat[cat] = []
    site_shannon_cat[cat] = []
    type_shannon_cat[cat] = []
    site_simpson_cat[cat] = []
    type_simpson_cat[cat] = []
    site_count_cat[cat] = []
    type_count_cat[cat] = []

wh_num = len(wh_bug_count)

print("wh_num = " + str(wh_num))

def catWH(wh, wh_count):

    # "equal_partition", "top_ones"
    cat_type = "top_ones"    
    
    if cat_type == "equal_partition":
        if wh_count < wh_num / 3:
            return "h"
        elif wh_count > wh_num / 3 * 2:
            return "l"
        else:
            return "m"
    elif cat_type == "top_ones":
        if wh_bug_count[wh] < 30:
            return "l"
        elif wh_bug_count[wh] > 70:
            return "h"
        else:
            return "m"        
    

def shannonIndex(data, total):
    total_count = 0        
    for item in data:
        total_count += data[item]
    
    shannon_index = 0
    for item in data:  
        p = data[item] / total_count
        shannon_index += - p * math.log(p)
    
    return shannon_index / math.log(total)
    
    
    #if len(data) == 1:
    #    return 1
    #return shannon_index / math.log(len(data))

def simpsonIndex(data, total):
    index = 0    
    
    total_count = 0        
    for item in data:
        total_count += data[item]    
    
    for item in data:
        p = data[item] / total_count
        index += p * p
    
    # return 1 / index / total
    
    return 1 / index / len(data)


wh_count = 0

for pair in sorted(wh_bug_count.items(), key=itemgetter(1),reverse=True):

    wh = pair[0]
    wh_count += 1
        
    cat = catWH(wh, wh_count)

    same_site_cat[cat].append(wh_same_site[wh])
    same_type_cat[cat].append(wh_same_type[wh])

    sh_site = shannonIndex(wh_site_dict[wh], len(all_site))
    sh_type = shannonIndex(wh_type_dict[wh], len(all_type))
    site_shannon_cat[cat].append(sh_site)
    type_shannon_cat[cat].append(sh_type)
    site_shannon.append(sh_site)
    type_shannon.append(sh_type)
    
    si_site = simpsonIndex(wh_site_dict[wh], len(all_site))
    si_type = simpsonIndex(wh_type_dict[wh], len(all_type))   
    site_simpson_cat[cat].append(si_site)
    type_simpson_cat[cat].append(si_type)
    site_simpson.append(si_site)
    type_simpson.append(si_type)    
    
    site_count_cat[cat].append(len(wh_site_dict[wh]))
    type_count_cat[cat].append(len(wh_type_dict[wh]))
    site_count.append(len(wh_site_dict[wh]))
    type_count.append(len(wh_type_dict[wh]))

matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize=10) 
matplotlib.rc('ytick', labelsize=10) 


# See: http://matplotlib.org/examples/pylab_examples/scatter_hist.html

nullfmt   = NullFormatter()  

left, width = 0.1, 0.65
bottom, height = 0.1, 0.65
bottom_h = left_h = left+width+0.02

rect_scatter = [left, bottom, width, height]
rect_histx = [left, bottom_h, width, 0.2]
rect_histy = [left_h, bottom, 0.2, height]


fit_transition = plt.figure(1, figsize=(6,6))

ax = fit_transition.add_subplot(111)

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)
ax.set_frame_on(False)

axScatter = plt.axes(rect_scatter)
axHistx = plt.axes(rect_histx)
axHisty = plt.axes(rect_histy)

# no labels
axHistx.xaxis.set_major_formatter(nullfmt)
axHisty.yaxis.set_major_formatter(nullfmt)


# We can have different scatter plots here

printer = "count"

xymax = 1.0

if printer == "transition":
    # Overall transition
    # axScatter.scatter(same_sites, same_types, color = "b")
    # Transition for different levels of white hats
    axScatter.scatter(same_site_cat["l"], same_type_cat["l"], color = "b")
    axScatter.scatter(same_site_cat["m"], same_type_cat["m"], color = "b")
    axScatter.scatter(same_site_cat["h"], same_type_cat["h"], color = "r")
    xLabel = r'$P_s$'
    yLabel = r'$P_t$'
elif printer == "shannon":
    # Shannon index for different levels of white hats
    axScatter.scatter(site_shannon_cat["l"], type_shannon_cat["l"], color = "b")
    axScatter.scatter(site_shannon_cat["m"], type_shannon_cat["m"], color = "g")
    axScatter.scatter(site_shannon_cat["h"], type_shannon_cat["h"], color = "r")
elif printer == "simpson":
    axScatter.scatter(site_simpson_cat["l"], type_simpson_cat["l"], color = "b")
    axScatter.scatter(site_simpson_cat["m"], type_simpson_cat["m"], color = "b")
    axScatter.scatter(site_simpson_cat["h"], type_simpson_cat["h"], color = "r")
elif printer == "count":
    axScatter.scatter(site_count_cat["l"], type_count_cat["l"], facecolors='none', edgecolors='b')
    axScatter.scatter(site_count_cat["m"], type_count_cat["m"], facecolors='none', edgecolors='b')
    axScatter.scatter(site_count_cat["h"], type_count_cat["h"], color = "r", marker = "^")
    #xymax = max(max(site_count), max(type_count))
    xLabel = "Number of Organizations"
    yLabel = "Number of Vuln. Types"
else:
    assert False

axScatter.set_xlabel(xLabel, fontsize=fontSize)
axScatter.set_ylabel(yLabel, fontsize=fontSize)

# plt.tick_params(labelsize=14)


if printer != "count":
    axScatter.set_xlim(0.0, xymax)
    axScatter.set_ylim(0.0, xymax)

# now determine nice limits by hand:
binwidth = 0.04
#xymax = np.max( [np.max(np.fabs(same_sites)), np.max(np.fabs(same_types))] )

lim = (int(xymax/binwidth) + 1) * binwidth

if printer != "count":
    xHistlim = lim
    yHistlim = lim
else:
    xHistlim = (int(max(site_count)/binwidth) + 1) * binwidth
    yHistlim = (int(max(type_count)/binwidth) + 1) * binwidth    
    print("Average site_count = " + str(sum(site_count) / len(site_count)))
    print("Average type_count = " + str(sum(type_count) / len(type_count)))

axScatter.set_xlim( (0, xHistlim) )
axScatter.set_ylim( (0, yHistlim) )

xbins = np.arange(0, xHistlim + binwidth, binwidth)
ybins = np.arange(0, yHistlim + binwidth, binwidth)


if printer == "transition":
    axHistx.hist(same_sites, bins=xbins,histtype="step")
    axHisty.hist(same_types, bins=ybins, orientation='horizontal',histtype="step")
elif printer == "shannon":
    axHistx.hist(site_shannon, bins=xbins,histtype="step")
    axHisty.hist(type_shannon, bins=ybins, orientation='horizontal',histtype="step")
elif printer == "simpson":
    axHistx.hist(site_simpson, bins=xbins,histtype="step")
    axHisty.hist(type_simpson, bins=ybins, orientation='horizontal',histtype="step")
elif printer == "count":
    axHistx.hist(site_count, bins=xbins,histtype="step")
    axHisty.hist(type_count, bins=ybins, orientation='horizontal',histtype="step")


axHistx.set_xlim( axScatter.get_xlim() )
axHisty.set_ylim( axScatter.get_ylim() )

#plt.show()

fit_transition.tight_layout()

fit_transition.savefig(transitionScatterPath) 








# TODO: See what this one is doing

#monthly_low_alexa_list = []
#for month in sorted(month_list):
#    monthly_low_alexa_list.append(monthly_low_alexa_dict[month])
    #print(month + ',' + str(monthly_low_alexa_dict[month]))

#pylab.bar(monthly_low_alexa_list)
#pylab.show()
    
    
    
    
# Need to start from 1, otherwise the log-log figure will
# ignore zeros!    
pos = np.arange(1, len(time_intervals_count) + 1)
width = 1     # gives histogram aspect to the bar diagram

fig_wh_time_interval = plt.figure()

ax = fig_wh_time_interval.add_subplot(111)

isLogLog = True

if isLogLog:
    ax.set_yscale('log')
    ax.set_xscale('log')

ax.set_ylabel(yLabel, fontsize=fontSize)
ax.set_xlabel(xLabel, fontsize=fontSize)

plt.plot(pos, time_intervals_count, color="b")

fig_wh_time_interval.tight_layout()

fig_wh_time_interval.savefig(intervalDistPath)    
    
    
    
for i in range(0, time_interval_cutoff):
    time_intervals.write(str(i) + "," + str(time_intervals_count[i]) + "\n")

time_intervals.close()
