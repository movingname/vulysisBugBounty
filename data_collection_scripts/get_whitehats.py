import urllib.request
import http.cookiejar
import time
import re
import traceback
from bs4 import BeautifulSoup
from pymongo import Connection


con = Connection()
db = con.wooyun_2
whitehats = db.whitehats

def is_page_url(tag):
    if tag.name != 'a':
        return False
    return tag['href'].find('/whitehats/') >= 0 and tag['href'].find('/whitehats/page') < 0 and tag['href'] != '/whitehats/'


cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
urllib.request.install_opener(opener)

maxPageNum = 80;

#f = open("whitehats_list.txt", "w")

error_count = 0;

whitehat_fields = ["registration_time", 'level', 'bug_num', 'elite_bug_num', 'rank_value']

for i in range(1, maxPageNum):

    try:
        whitehat_url = "http://www.wooyun.org/whitehats/page/" + str(i)
        print(whitehat_url)
        req = opener.open(whitehat_url)
        soup = BeautifulSoup(req.read())        
        
        page_url = soup.find_all(is_page_url)
        for url in page_url:
            whitehat_item = {}
            whitehat_item['name'] = url.string
            
            wh_find = whitehats.find_one({'name': whitehat_item['name']})
            if wh_find != None:
                #print("Warning: " + whitehat_item['name'] + " already exists.")
                continue         
            
            children = url.parent.parent.contents
            field_count = 0
            for tag in children:
                if(tag.name == 'th'):
                    whitehat_item[whitehat_fields[field_count]] = tag.string
                    field_count = field_count + 1
    
            
            # Skip a special case
            if len(whitehat_item) == 1:
                continue
                
            #print(whitehat_item)
            
            whitehats.insert(whitehat_item)
    except:
        print('error at ' + str(i))
        error_count = error_count + 1
    time.sleep(1)

print('error_count = ' + str(error_count))

#f.close()

#

#

#links=soup('a')
