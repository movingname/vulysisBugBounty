import urllib.request
import http.cookiejar
import time
import random
import socket
import os

socket.setdefaulttimeout(10)

isOnlyNew = True

cj = http.cookiejar.CookieJar()

#We create an opener which could be used to add cookie, user-agent, etc.

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]

urllib.request.install_opener(opener)


report_folder = "E:/WooyunProject/reports/reports/"

saved_ids = []

# TODO: sort the files based on name

for root, subFolders, files in os.walk(report_folder):
    for f in files:
        saved_ids.append(f.split('.')[0])

f = open("../data/bug_url_list.txt", "r")

url_count = 0

# This is not exactly nessasary. Could save sometime tough.
url_count_start = 0

new_saved_count = 0

# TODO: put this into a function, so 
#       we can choose to call this
#       or call missing check
for url in f:
    url_count += 1
    if url_count < url_count_start:
        continue
    
    print(url_count)
    print(url)    
    
    strs = url.split("/")
    bug_id = strs[len(strs) - 1].strip()

    if isOnlyNew:    
        if bug_id in saved_ids:
            print("Already saved.")
            continue
    try:
 
        # See: https://docs.python.org/3/library/urllib.request.html#urllib.request.urlretrieve
        urllib.request.urlretrieve(url, report_folder + bug_id + '.html')

        new_saved_count += 1

    except:
        
        print("Exception at " + url)
        
        # The request will block after certain period of time. 
        # We still don't know why. The current solution is to set
        # a global timeout and then reconnect. But there will be some 
        # missing pages, and we need to do one or multiple rounds of 
        # missing check to download those missing pages.
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]
        urllib.request.install_opener(opener)
        
    time.sleep(1 + random.random())

# TODO: after the run, check whether some urls are missing.

print("Crawling done.")
print("New saved count: " + str(new_saved_count))

