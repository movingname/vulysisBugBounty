import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import codecs
import time


url = "https://hackerone.com/programs"
#local_copy = "Programs - HackerOne.html"

local_copy = "../input/Directory_ Report Vulnerabilities to Companies's Security Teams.html"

# Currently, one should download the programs page manually and then
# use this script to parse the local copy. This is probability because
# the page contains javascript code which later fetches
# the list of the programs. Our crawler thus cannot get the information directly.
# Also, if you click view source in Chrome, you won't see the
# programs either.
getDataOnline = False

resultFilePath = "../output/programList.txt"
resultFile = codecs.open(resultFilePath, "w", "utf-8", buffering=0)

programStatFile = codecs.open("../output/programStat.txt", "w", "utf-8", buffering=0)

def is_program_name(tag):
    #print(tag)
    return  tag.name == 'span' and 'itemprop' in tag.attrs and "data-reactid" in tag.attrs

def is_program_link(tag):
    
    return tag.name == "a" and 'class' in tag.attrs and 'spec-program-name' in tag.attrs['class']


# HackerOne has changed their website. So we cannot use the following code anymore.
# Or we need to use some interaction simulation to get the pop up window.

#def is_item_value(tag):
#    return  tag.name == 'div' and 'class' in tag.attrs and "program-profile-meta-item-value" in tag.attrs['class']
    
#def is_bug_closed(tag):
#    if (tag.name != "div") or ('class' not in tag.attrs) or ("program-profile-meta-item-value" not in tag.attrs['class']):
#        return False
#    print(tag)
#    return True
    

if getDataOnline:

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0')]
    urllib.request.install_opener(opener)
    req = opener.open(url)

    while req.code != 200:
        print("Request fail, code = " + str(req.code))
        time.sleep(5)
        req = opener.open(url)

    soup = BeautifulSoup(req.read())

else:

    soup = BeautifulSoup(codecs.open(local_copy, encoding="utf-8").read())

entries = soup.find_all(is_program_link)

for entry in entries:

    #bugClosedTag = entry.parent.parent.findNext(is_item_value)

    #bugClosed = bugClosedTag.string
    
    #progName = entry.findNext("span").string
    
    progLink = entry['href']
    progName = entry.findNext(is_program_name).string
    
    minBounty = None

    #if "Minimum bounty" in str(bugClosedTag.parent.parent):
    #    minBounty = bugClosedTag.findNext(is_item_value).string

    #programStatFile.write(progName + "," + bugClosed + "," + str(minBounty) + "\n")

    print(progLink)

    resultFile.write(progName + "," + progLink + "\n")

resultFile.close()
programStatFile.close()



