from pymongo import MongoClient
import codecs
import operator
from datetime import datetime
from libwooyun import alexa_levels, catStatType, stat_type

con = MongoClient()
db = con.wooyun_2
bugs = db.bugs
corp_reports = db.corp_reports
corp_alexa = db.corp_alexa

corp_stat_raw_count = {}

corp_resp_raw_count = {}

no_resp_raw = {}

bug_count = 0
no_resp_count = 0
no_stat_count = 0
no_confirm_time_count = 0
resp_len_count = {}

ignore_resp_count = 0
ignore_noresp_count = 0

alexa_count = {}
alexa_stat_count = {}
for alexa in alexa_levels:
    alexa_stat_count[alexa] = {}
    alexa_count[alexa] = 0
    for stat in stat_type:
        alexa_stat_count[alexa][stat] = 0



corp_stat_count = {}
for stat in stat_type:
    corp_stat_count[stat] = 0


for bug in bugs.find():

    bug_count += 1

    corp = bug["corp"]
    wh = bug["whitehat"]
    
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
    
    alexa_count[alexa_group] += 1    
    
    response = None    
    
    if "corp_response" in bug:
        # The response is different for each report.
        # We can do some simple word statistics, such 
        # as counting the number of "感谢".        
        response = bug["corp_response"]
        if response not in corp_resp_raw_count:
            corp_resp_raw_count[response] = 0
        corp_resp_raw_count[response] += 1
    else:
        no_resp_count += 1
   
    if "status" in bug:  
        status = bug["status"]
        if status not in corp_stat_raw_count:
            corp_stat_raw_count[status] = 0
        corp_stat_raw_count[status] += 1
        
        stat = catStatType(status, response)        
        
        corp_stat_count[stat] += 1
        
        alexa_stat_count[alexa_group][stat] += 1
        
        if "忽略" in status:
            if response != None:
                ignore_resp_count += 1
                # TODO: we can do some text analysis of the response.
                #print(response)
            else:
                ignore_noresp_count += 1

    else:
        no_stat_count += 1

    if "confirm_time" in bug:     
        report_time = datetime.strptime(bug["submit_time"], "%Y-%m-%d %H:%M")
        
        if bug["confirm_time"] == "\n危害等级":
            print("Error")
            continue
        confirm_time = datetime.strptime(bug["confirm_time"], "%Y-%m-%d %H:%M")
        diff_time = confirm_time - report_time
        diff_days = diff_time.days
        if diff_days not in resp_len_count:
            resp_len_count[diff_days] = 0
        resp_len_count[diff_days] += 1
    else:
        no_confirm_time_count += 1
print("Total bug count = " + str(bug_count))
print("No response count = " + str(no_resp_count))
print("No status count = " + str(no_stat_count))
print("No confirm time count = " + str(no_confirm_time_count))
print("Ignore but reponded count = " + str(ignore_resp_count))
print("Ignore and no repond count = " + str(ignore_noresp_count))

assert no_resp_count == no_confirm_time_count
print(corp_stat_raw_count)


#print(corp_stat_count)

#print(corp_resp_raw_count)

print("\nPercentage of response types:")
for stat in corp_stat_count:
    print(stat + ": " + str("{0:.2f}".format(corp_stat_count[stat] / bug_count)))

print(resp_len_count)

alexa_stat_percent = {}

for alexa in alexa_levels:
    alexa_stat_percent[alexa] = {}
    for stat in stat_type:
        alexa_stat_percent[alexa][stat] = alexa_stat_count[alexa][stat] / alexa_count[alexa]

print(alexa_stat_percent)

#print(alexa_stat_count)