
from pymongo import Connection

con = Connection()
db = con.wooyun_2
bugs = db.bugs
corps = db.corps
reports = db.whitehat_reports

whitehat_reports = {}

corp_not_found_count = 0;

bug_count = 0;

for bug in bugs.find():

    #print(bug['name'])
    
    if not bug['whitehat'] in whitehat_reports:
        whitehat_reports[bug['whitehat']] = []

    report = {}
    
    report["bug_id"] = bug['bug_id']    
    report["time"] = bug['submit_time']
    report["corp"] = bug['corp'].strip()
    report["self_threat_level"] = bug['self_threat_level']
    if "corp_threat_level" in bug:
        report["corp_threat_level"] = bug['corp_threat_level']
    else:
        report["corp_threat_level"] = 'unknown'
    if 'bug_type' in bug:
        report['bug_type'] = bug['bug_type']
    else:
        report['bug_type'] = 'unknown'
        
    corp = corps.find_one({'name': report["corp"]})

    if(corp == None):
        corp_not_found_count = corp_not_found_count + 1

    whitehat_reports[bug['whitehat']].append(report)
    
    bug_count = bug_count + 1;
    #print(bug_count)



print(str(corp_not_found_count) + ' bugs for unregistered corps.')





for whitehat in whitehat_reports.keys():

    item = {}
    item['whitehat'] = whitehat
    item['report'] = whitehat_reports[whitehat]
    
    reports.insert(item)
    #f = open('whitehat_reports\\' + whitehat, 'w')
    #for report in whitehat_reports[whitehat]:
    #    f.write(report["time"] + ',' + report["threat_level"] + ',' + report['corp'] + '\n')
    #f.close()



