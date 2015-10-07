'''

This script tries to find an url for a corp in Wooyun database. We use Google's first search result as the url.
Apparently there will be errors so please manually filter them out!

The Google search code is obtained from (with some modifications):
http://stackoverflow.com/questions/1657570/google-search-from-a-python-app
https://breakingcode.wordpress.com/2010/06/29/google-search-python/

'''


from pymongo import Connection
import time
import os
from google import search
import json
import urllib.request, urllib.parse
import codecs


con = Connection()
db = con.wooyun_2
bugs = db.bugs
corps = db.corps
reports = db.corp_reports

f_corp_url = '../data/corp_url_list.txt'


#This version will get blocked after around 10 requests.
def get_url_from_google_old(searchfor):
  query = urllib.parse.urlencode({'q': searchfor})
  url = 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&%s' % query
  search_response = urllib.request.urlopen(url)
  search_results = search_response.read().decode("utf8")
  results = json.loads(search_results)
  data = results['responseData']
  #print('Total results: %s' % data['cursor']['estimatedResultCount'])
  hits = data['results']
  return hits[0]['url']
  #print('Top %d hits:' % len(hits))
  #for h in hits: print(' ', h['url'])
  #print('For more results, see %s' % data['cursor']['moreResultsUrl'])

def get_url_from_google(searchfor):
    for url in search(searchfor, stop=1):
        return url

known_url_corp_set = []

if os.path.isfile(f_corp_url):
    f_list = codecs.open(f_corp_url, 'r', 'utf-8')
    for line in f_list:
        known_url_corp_set.append(line.split('\t')[0])
    f_list.close()


f_list = codecs.open(f_corp_url, 'a', 'utf-8',buffering=0)


#First, we output corp and url pairs that are in registered list.

for corp in corps.find():
    if corp['name'] not in known_url_corp_set:
        f_list.write(corp['name'] + '\t' + corp['url'] + '\n')
        known_url_corp_set.append(corp['name'])

print('We already know ' + str(len(known_url_corp_set)) + ' corps\' url.')

#Second, we use google to find corps we do not know their urls

unknown_count = 0

for report in reports.find():
    name = report['corp']

    if name == "":
        #We skip this special case for now
        continue
    
    if name not in known_url_corp_set:
        try:
            print('Search for ' + name)
            url = get_url_from_google(name)
            f_list.write(name + '\t' + url + '\n')
            f_list.flush()
            print(name + '\t' + url)
            unknown_count = unknown_count + 1
            #Sleep one second because we do not want to piss off Google
            time.sleep(1)
        except:
            print("An error occured at " + name)

print('We find url for ' + str(unknown_count) + ' corps')

f_list.close()




