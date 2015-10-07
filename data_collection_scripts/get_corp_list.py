import urllib.request
import http.cookiejar
import time
from bs4 import BeautifulSoup
import codecs

# This script will hang during crawling.
# At that time we need the append mode,
# and also set the startPageNum to be the hang page.
isAppendMode = False


def is_page_url(tag):
    if tag.name != 'a':
        return False
    if tag['href'].find('/corps/') >= 0 and tag['href'].find('#comment') < 0:
        if tag['href'] == "/corps/":
            return False
        elif tag['href'].find('/corps/page/') >= 0:
            return False
        return True
    return False


cj = http.cookiejar.CookieJar()

# We create an opener which could be used to add cookie, user-agent, etc.
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]

urllib.request.install_opener(opener)

startPageNum = 1

# Need to manually obtain this.
maxPageNum = 39

URLCount = 0


if isAppendMode:
    f = codecs.open("../data/corp_list.txt", "a", "utf-8")
else:
    f = codecs.open("../data/corp_list.txt", "w", "utf-8")

for i in range(startPageNum, maxPageNum):
    bug_page_url = "http://www.wooyun.org/corps/page/" + str(i)
    print(bug_page_url)
    req = opener.open(bug_page_url)
    print(req.code)
    soup = BeautifulSoup(req.read())
    page_url = soup.find_all(is_page_url)
    for url in page_url:
        #print(url)
        corp_name = url['href'].split("/")[2]
        corp_url = url.parent.findNext("td").a['href']
        f.write(corp_name + ',' + corp_url + '\n')
        print(corp_name + ',' + corp_url)
        f.flush()
        URLCount += 1
    print("URLCount = " + str(URLCount))
    # It seems that Wooyun has anti-DDOS or crawling, 
    # so we want to set this value to be larger.
    time.sleep(2)

f.close()

#

#

#links=soup('a')
