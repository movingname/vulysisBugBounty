'''
Analyse all bug reports (bugs collection) and generate corp reports (corp_reports collection)

'''

from pymongo import Connection


con = Connection()
db = con.wooyun_2
bugs = db.bugs
corps = db.corps
reports = db.corp_reports

corp_reports = {}

corp_bug_count = {}

corp_unique_whitehats = {}

# corp_alexa = {}

corp_url = {}

corp_not_found_count = 0;

bug_count = 0;

for bug in bugs.find():

    #print(bug['name'])
	
    if not bug['corp'] in corp_reports:
        corp_reports[bug['corp']] = []
        corp_unique_whitehats[bug['corp']] = []
        corp_bug_count[bug['corp']] = 0
        #corp_alexa[bug['corp']] = 'unknown'
	
    if not bug['whitehat'] in corp_unique_whitehats[bug['corp']]:
        corp_unique_whitehats[bug['corp']].append(bug['whitehat'])
	
    corp_bug_count[bug['corp']] = corp_bug_count[bug['corp']] + 1
    
    report = {}
    
    report["time"] = bug['submit_time']
    report["name"] = bug['name']
    report["bug_id"] = bug['bug_id']
    report["whitehat"] = bug['whitehat'].strip()
    report["self_threat_level"] = bug['self_threat_level']
    if "corp_threat_level" in bug:
        report["corp_threat_level"] = bug['corp_threat_level']
    else:
        report["corp_threat_level"] = 'unknown'
    report["bug_id"] = bug['bug_id']
    if 'bug_type' in bug:
        report['bug_type'] = bug['bug_type']
    else:
        report['bug_type'] = 'unknown'
        
    corp = corps.find_one({'name': bug['corp']})

    if(corp == None):
        corp_not_found_count = corp_not_found_count + 1      

    corp_reports[bug['corp']].append(report)
    
    bug_count = bug_count + 1;
    #print(bug_count)



print(str(corp_not_found_count) + ' bugs for unregistered corps.')





for corp in corp_reports.keys():

    item = {}
    item['corp'] = corp
    item['report'] = corp_reports[corp]
    item['bug_count'] = corp_bug_count[corp];
    item['white_count'] = len(corp_unique_whitehats[corp])
    #item['corp_rank'] = corp_alexa[corp]
    
    #Insert to database
    reports.insert(item)



