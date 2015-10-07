import urllib.request
import http.cookiejar
import random
import socket
import time
import os
from bs4 import BeautifulSoup

# This script will hang during crawling.
# At that time we need the append mode,
# and also set the startPageNum to be the hang page.
isAppendMode = True


def is_page_url(tag):
    if tag.name != 'a':
        return False
    return tag['href'].find('/bugs/wooyun-20') >= 0 and tag['href'].find('#comment') < 0


cj = http.cookiejar.CookieJar()

# We create an opener which could be used to add cookie, user-agent, etc.
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]

urllib.request.install_opener(opener)

startPageNum = 1

# Need to manually obtain this from Wooyun's page.
maxPageNum = 3256



urlList = []



if isAppendMode:
    
    f = open("../data/bug_url_list.txt", "r")    
    for line in f:
        urlList.append(line.strip())
    f.close()
    
    f = open("../data/bug_url_list.txt", "a")
else:
    f = open("../data/bug_url_list.txt", "w")


firstPage = True
totalNewBugCount = 0
exceptionCount = 0

exceptions = []
incompleteLists = []

for i in range(startPageNum, maxPageNum):
    
    try:
        bug_page_url = "http://www.wooyun.org/bugs/page/" + str(i)
        print(bug_page_url)
        req = opener.open(bug_page_url)
        print(req.code)
        soup = BeautifulSoup(req.read())
        page_url = soup.find_all(is_page_url)
        
        if firstPage:
            firstPage = False
        else:
            incompleteLists.append(i)
        
        alreadyExistCount = 0
        for url in page_url:
            
            fullURL =  'http://www.wooyun.org' + url['href']       
            
            if fullURL in urlList:
                #print("Already exisit: " + fullURL)
                alreadyExistCount += 1
                continue
            #print(url)
            f.write(fullURL + '\n')
            f.flush()
            totalNewBugCount += 1
        print("totalNewBugCount = " + str(totalNewBugCount))
        print("alreadyExistCount = " + str(alreadyExistCount))
        print("exceptionCount = " + str(exceptionCount))
        # It seems that Wooyun has anti-DDOS or crawling, 
        # so we want to set this value to be larger.
        time.sleep(1)
        
    except:
        
        # The connection will occasionally break.
        # So we want to recover.        
        
        # TODO: a downside of capturing any exception is that
        # we cannot use the keyboard to abort the script.
        
        print("Exception at i = " + str(i))    
        exceptionCount += 1
        exceptions.append(i)
        
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        urllib.request.install_opener(opener)
        
f.close()

# Suppose to rerun them
print("exceptions: " + str(exceptions))
print("incompleteLists: " + str(incompleteLists))

