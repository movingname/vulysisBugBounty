import math
from scipy.stats import chi2, norm


severities = ["高", "中", "低"]

sev_colors = {"高":"r", "中":"yellow", "低":"chartreuse"}

# Since we usually do not have the complete data for the last month.
# We decide to skip it.
last_skip_month = "2015-02"

alexa_levels = ["1-200", "201 - 2000", ">2000"]

stat_type = {"Active ignore", "No response", "Handled by third parties", 
             "Confirmed by the organization", "Other"}

wh_black_list = {"路人甲"}		

corp_black_list = {"", "cncert国家互联网应急中心"}	 
			 
# Use this function to further merge similar bug types    
def mergeBugType(bug_type):
    if bug_type == "Remote Code Execution":
        return "Code Execution"
 
    if "Weak Password" in bug_type:
        return "Weak Password"
        
    if "Information Leakage" in bug_type:
        return "Sensitive Information Leakage"
       
    return bug_type

def shortenBugType(bug_type):

    if bug_type == 'Unauthorized Access/Privilege Escalation':
        return "Unauth. Access/Priv. Esc."

    if bug_type == "System/Service Misconfiguration":
        return "System/Service Misconfig."
        
    if bug_type == "Sensitive Information Leakage":
        return "Sensitive Info. Leakage"

    return bug_type

def catStatType(stat, response=None):
    if "忽略" in stat:
        if response != None:
            return "Active ignore"
        else:
            return "No response"
    elif "第三方" in stat:
        return "Handled by third parties" 
    elif "确认" in stat or "修复" in stat:
        return "Confirmed by the organization"
    else:
        return "Other"

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

        
# itemList: a list of         
def trendTest(itemList, itemElapsedTime, transDict = None, test = "Laplace", skip_list = []):

    printIndividual = False

    increaseList = []
    decreaseList = []
    cantsayList = []
    
    for item in itemList:

        if item in skip_list:
            continue

        itemID = item
        if transDict:
            itemID = transDict[item]
            
        chi_square = 0
        lap_z = 0
        t_end = itemElapsedTime[itemID][len(itemElapsedTime[itemID]) - 1]
        r = len(itemElapsedTime[itemID]) - 1    
        for tp in itemElapsedTime[itemID]:
    
            # has to skip the first failure for chi_square.
            if tp == 0:
                continue
            
            chi_square += math.log(t_end / tp)   
            
            lap_z += (tp - t_end / 2)
    
        chi_square *= 2
        
        lap_z = lap_z * math.sqrt(12 * r) / r / t_end
    
        if test == "Chi Square":
            stat = chi_square
            conf90, conf95 = chi2.ppf([0.9, 0.95], 2 * r)
            if stat >= conf95:
                if printIndividual:
                    print(item + ": decrease with 0.95 conf.")
                decreaseList.append(item)
            else:
                if printIndividual:
                    print(item + ": can't say.")  
                cantsayList.append(item)
        elif test == "Laplace":
            stat = lap_z
            conf5, conf90, conf95 = norm.ppf([0.05, 0.9, 0.95])
    
            if stat >= conf95:
                if printIndividual:
                    print(item + ": increase with 0.95 conf.")
                increaseList.append(item)
            elif stat < conf5:
                if printIndividual:
                    print(item + ": decrease with 0.95 conf.")
                decreaseList.append(item)
            else:
                if printIndividual:
                    print(item + ": can't say.")  
                cantsayList.append(item)
    
        #print(prog + " stat = " + str(stat)
        #       + " [0.9, 0.95] = " + [conf90, conf95])
    
    print(str(len(decreaseList)) + " programs have decreasing trends with conf 0.95.")
    print(str(len(increaseList)) + " programs have increasing trends with conf 0.95.")
    print(str(len(cantsayList)) + " programs cannot be said to have trends.")