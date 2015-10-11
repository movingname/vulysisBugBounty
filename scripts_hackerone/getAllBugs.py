import urllib.request
import http.cookiejar
from bs4 import BeautifulSoup
import codecs
import time
import operator

# TODO: Get the bug count from the program page so we can cross check the
# data integrity.




disableRewardMatching = True

programListFile = open("../output/programList.txt")

resultFile = codecs.open("../output/allbugs.txt", "w", "utf-8", buffering=0)
allBountyFile = codecs.open("../output/allBounties.txt", "w", "utf-8", buffering=0)
progWhCountFile = codecs.open("../output/progWhCount.txt", "w", "utf-8", buffering=0)


def is_hacktivity_container_subject(tag):
    return  tag.name == 'div' and 'class' in tag.attrs and "hacktivity-container-subject" in tag.attrs['class']

def is_hacktivity_entry(tag):
    return  tag.name == 'div' and 'class' in tag.attrs and "hacktivity-container-subject-entry" in tag.attrs['class']

def is_hacktivity_timestamp_link(tag):
    return  tag.name == 'a' and 'class' in tag.attrs and "hacktivity-timestamp-link" in tag.attrs['class']

def is_profile_stats_item(tag):
    return  tag.name == 'li' and 'class' in tag.attrs and "profile-stats-item" in tag.attrs['class']

def is_profile_stats_amount(tag):
    return  tag.name == 'div' and 'class' in tag.attrs and "profile-stats-amount" in tag.attrs['class']

def is_profile_header_title(tag):
    return  tag.name == 'h1' and 'class' in tag.attrs and "profile-header-title" in tag.attrs['class']


# TODO: basically, we can assume that the bug name shall not equal to any
# program name
nonBugList = ["Phabricator"]

allbugs = []
allrewards = []
numExpectedBugs = 0
numRewardNotMatch = 0
numBugNoReward = 0
numBugNumberInconsistent = 0
bugNumberInconsistentProgs = []

progWhCount = {}

for string in programListFile:
    
    strs = string.split(",")    
    
    progName = strs[0]
    url = "https://hackerone.com" + strs[1].strip()
    
    bugs = []

    rewards = []

    bug_expected = None
    
    whCount = None
    
    

    #url = "https://hackerone.com/phabricator?show_all=true"

    
    
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent','Mozilla/5.0 (Windows NT 6.3; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0')]
    urllib.request.install_opener(opener)

    pageNum = 1

    while True:

        req = opener.open(url + "?page=" + str(pageNum))
        
    
        while req.code != 200:
            print("Request fail, code = " + str(req.code))
            time.sleep(5)
            req = opener.open(url)
    
        soup = BeautifulSoup(req.read())
    
    
        if pageNum == 1:    
    
            entries = soup.find_all(is_profile_stats_item)
            
            for entry in entries:
                if ("Reports closed" in str(entry)) or ("Report closed" in str(entry)):
                    amount = entry.find(is_profile_stats_amount)
                    bug_expected = int(amount.string)
                    
                    if bug_expected == None:
                        print(entry)
                    
                elif ("Hackers thanked" in str(entry)) or ("Hacker thanked" in str(entry)):
                    amount = entry.find(is_profile_stats_amount).string
                    whCount = int(amount)
        
            assert bug_expected != None
            numExpectedBugs += bug_expected
        
            titleTag = soup.find(is_profile_header_title)
            assert whCount != None
            progWhCount[progName] = whCount
            print(progName)
    
        entries = soup.find_all(is_hacktivity_container_subject)

        if len(entries) == 0:
            break
   
        for entry in entries:
            #print(entry)
    
            hacktivity = entry.find(is_hacktivity_entry)
    
            item = {}
    
            # The default is for the resolved type of events
            siteIndex = 0
            bugIndex = 1
            whIndex = 2
            items = bugs
            eventType = 0
            
            if "with swag." in str(entry):
                # TODO: handle this type of entry            
                continue
    
            # The indexes are slightly different for rewarded type of events
            if "rewarded" in str(entry) and "bounty" in str(entry):
                whIndex = 1
                bugIndex = 2
                items = rewards
                eventType = 1
    
            if "resolved a report" in str(entry):
                bugIndex = -1
                whIndex = 1
    
            linkCount = 0
    
            for content in hacktivity.contents:
                
                if content.name == "a":
                    if linkCount == siteIndex:
                        item["site"] = content.string
                        item["site_link"] = content["href"]
                    elif linkCount == bugIndex:
                        if content.string in nonBugList:
                            continue
                        item["bug"] = content.string
                        item["bug_link"] = content["href"]
                    elif linkCount == whIndex:
                        item["wh"] = content.string
                        item["wh_link"] = content["href"]
                    linkCount += 1
                elif content.name == "strong":
                    item["bounty"] = content.string
            
            if eventType == 1 and not "bounty" in item:
                item["bounty"] = "Unknown"
    
            # See https://docs.python.org/3.3/library/time.html
            # for more information related to time in python
                    
            timestamp = entry.find(is_hacktivity_timestamp_link).contents[0]["title"]
            timeParsed = time.strptime(timestamp, "%B %d, %Y %H:%M:%S +0000")
            item["time"] = time.strftime("%Y-%m-%d %H:%M:%S", timeParsed)
    
            #activityID = timestamp["href"][10:]
            #item["activityID"] = activityID
    
            if not "site" in item:
                if "time" in item:
                    print("start time is " + item["time"])
                continue
    
            assert "wh" in item
    
            items.append(item)
            
            #try:
            #    items[item["activityID"]] = item
            #except:
            #    print(item)
    
        # Now, we try to associate rewards with bugs.
        for reward in sorted(rewards, key=lambda k: k['time']):
            reward["match"] = False
            # See: http://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python
            for bug in sorted(bugs, key=lambda k: k['time']):
                if "match" in bug:
                    continue
    
                # If the reward has a bug_link, we can find the
                # bug that has the same bug_link
                if "bug_link" in reward:
                    if "bug_link" in bug:
                        if reward["bug_link"] == bug["bug_link"]:
                            reward["match"] = True
                            bug["match"] = True
                # If the reward does not have a bug_link, we use find
                # the earliest non match bug.
                else:
                    if (not "match" in bug and not "bug_link" in bug
                        and reward["wh"] == bug["wh"]):
                        reward["match"] = True
                        bug["match"] = True                
                if reward["match"]:
                    bug["bounty"] = reward["bounty"]
                    bug["reward_time"] = reward["time"]
                    break
            if reward["match"] == False and not disableRewardMatching:
                print("WARNING: reward at time " + reward["time"] + " for " + reward["wh"] + " not matched")
                numRewardNotMatch += 1
                #print(reward)
    

            

    
        pageNum += 1
        time.sleep(1)

    for bug in bugs:
        allbugs.append(bug)

    for reward in rewards:
        allrewards.append(reward)
        
    print(len(bugs))

    if len(bugs) != bug_expected:
        print("Error: bug number inconsistent!")
        numBugNumberInconsistent += 1        
        bugNumberInconsistentProgs.append(progName)
    #break

#print(allrewards)


for bug in sorted(allbugs, key=lambda k: k['time']):
    resultFile.write(bug["time"] + ",; ")
    resultFile.write(bug["site"] + ",; " + bug["site_link"] + ",; ")
    resultFile.write(bug["wh"] + ",; " + bug["wh_link"] + ",; ")
    if "bug" in bug:
        resultFile.write(bug["bug"] + ",; " + bug["bug_link"] + ",; ")
    if "bounty" in bug and not disableRewardMatching:
        resultFile.write(bug["bounty"] + ",; " + bug["reward_time"])
    else:
        resultFile.write("None")
        numBugNoReward += 1
    resultFile.write("\n")

        
        
for reward in sorted(allrewards, key=lambda k: k['time']):
    allBountyFile.write(reward["time"] + ",; ")
    allBountyFile.write(reward["site"] + ",; " + reward["site_link"] + ",; ")
    allBountyFile.write(reward["wh"] + ",; " + reward["wh_link"] + ",; ")
    allBountyFile.write(reward["bounty"])
    allBountyFile.write("\n")

print("Crawling donw. Here are statistics:")
print("Total bug: " + str(len(allbugs)))
print("Total bug expected: " + str(numExpectedBugs))
print("Total reward: " + str(len(allrewards)))
print("Number rewards not match: " + str(numRewardNotMatch))
print("Number bugs no reward: " + str(numBugNoReward))
print("Number program bug number inconsistent: " + str(numBugNumberInconsistent))
print("bugNumberInconsistentProgs: " + str(bugNumberInconsistentProgs))


for pair in sorted(progWhCount.items(), key=operator.itemgetter(1), reverse=True):
    progWhCountFile.write(pair[0] + "," + str(pair[1]) + "\n")


programListFile.close()
resultFile.close()
allBountyFile.close()
progWhCountFile.close()