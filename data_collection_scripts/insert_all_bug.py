import urllib.request
import http.cookiejar
import time
from bs4 import BeautifulSoup
from pymongo import Connection
import os
import codecs

con = Connection()
db = con.wooyun_2   #Modify the database name for new data crawling task.
bugs = db.bugs


isFromOnline = False


# So here, I am trying to directly get locally unparsable
# files from Online. However, they are still unparsable...
isFromOnlineFailParsingOnly = False

if isFromOnlineFailParsingOnly:
    assert isFromOnline


report_folder = "E:/WooyunProject/reports/reports/"

reports = []

for root, subFolders, files in os.walk(report_folder):
    for f in files:
        reports.append(os.path.join(root,f))


bug_url = 'http://www.wooyun.org/bugs/'
corp_url = 'http://www.wooyun.org/corps/'
corp_url_len = len(corp_url)
whitehat_url = 'http://www.wooyun.org/whitehats/'
whitehat_url_len = len(whitehat_url)
bug_id_url = 'bugs/wooyun-20'
bug_id_url_len = len(whitehat_url)


#We create a lot of selectors

def is_bug_name(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('漏洞标题') >= 0

# If a tag contains another tag, then the string field will not work
# See: http://www.crummy.com/software/BeautifulSoup/bs4/doc/#string
def is_bug_name_with_cloud(tag):
    if tag.name != 'h3':
        return False
    if tag.strings == None:
        return False
    for string in tag.strings:
        if string.find('漏洞标题') >= 0:
            return True
    return False

def is_bug_corp(tag):
    return  tag.name == 'a' and tag['href'].find(corp_url) >= 0

def is_whitehat(tag):
    return  tag.name == 'a' and tag['href'].find(whitehat_url) >= 0

def is_bug_id(tag):
    return  tag.name == 'a' and tag['href'].find(bug_id_url) >= 0

def is_submit_time(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('提交时间') >= 0

def is_public_time(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('公开时间') >= 0

def is_confirm_time(tag):
    return  tag.name == 'p' and tag.string != None and tag.string.find('确认时间：') >= 0

def is_ignore_time(tag):
    return  tag.name == 'p' and tag.string != None and tag.string.find('忽略时间：') >= 0

def is_self_threat_level(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('危害等级：') >= 0

# The of corp threat level uses p tag while the self threat level uses h3 tag.
def is_corp_threat_level(tag):
    return  tag.name == 'p' and tag.string != None and tag.string.find('危害等级：') >= 0

def is_status(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('漏洞状态') >= 0

def is_bug_type(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('漏洞类型') >= 0

def is_self_rank(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('自评Rank') >= 0



# This is the rank given by the corp in most cases.
# In rare case (e.g. WooYun-2011-03494), this rank is given by Wooyun.
def is_corp_rank(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('漏洞Rank') >= 0

def is_corp_response(tag):
    return  tag.name == 'h3' and tag.string != None and tag.string.find('厂商回复') >= 0 

def is_reply_whitehat(tag):
    return  tag.name == 'a' and 'target' in tag.attrs and tag['href'].find(whitehat_url) >= 0

def is_reply_id(tag):
    return  tag.name == 'span' and 'class' in tag.attrs and "floor" in tag.attrs['class']

def is_bug_tag(tag):
    return  tag.name == 'span' and 'class' in tag.attrs and "tag" in tag.attrs['class']

#and tag.attrs['class'] == 'floor' and tag.string.find('#') >= 0


#def is_attention_num(tag):
#    return  tag['id'] == 'attention_num'

#We use this function to skip tabs, spaces, etc.
def get_longest_string(strs):
    longest_str = "";
    for str in strs:
        if len(str) > len(longest_str):
            longest_str = str
    return longest_str

no_response_strs = ['漏洞已经通知厂商但是厂商忽略漏洞',
                    '正在联系厂商或者等待认领',
                    '未能联系到厂商或者厂商积极拒绝',
                    '未联系到厂商或者厂商积极忽略']

# These bug reports are inconsistent, so we have to explicitly handle them
no_response_bug_ids = ['WooYun-2012-07040', 'WooYun-2012-06969', 'WooYun-2012-06967', 
                       'WooYun-2012-06958', 'WooYun-2012-06892', 
                       'WooYun-2012-06865', 'WooYun-2012-06820', 
                       'WooYun-2012-06644', 'WooYun-2012-06643', 
                       'WooYun-2012-04566', 'WooYun-2012-04179', 
                       'WooYun-2011-03494', 'WooYun-2011-03468', 
                       'WooYun-2013-21388', 'WooYun-2013-22322', 
                       'WooYun-2011-03058', 'WooYun-2011-03423',
                       "WooYun-2011-02032"]

# TODO: Need to figure out why they fail. Python will print out them in luanma.
#       So I guess there could be some encoding issues.
# TODO: We probably can recrawl them
parsing_fail_files = ['E:/WooyunProject/reports/reports/wooyun-2014-059339.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-071725.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-075083.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-075096.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-077249.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080340.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080356.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080613.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080862.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080865.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080879.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080884.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-081568.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082280.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082379.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082457.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082915.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082922.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-083216.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-085218.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-085774.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-086245.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-088069.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-088150.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-088195.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-088882.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-089309.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-061899.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-079879.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-079890.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-080064.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-081000.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-081339.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-081766.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-081915.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-082335.html',
                      'E:/WooyunProject/reports/reports/wooyun-2014-088188.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100097.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100503.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100566.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100599.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100606.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100738.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100781.html',
                      'E:/WooyunProject/reports/reports/wooyun-2015-0100809.html']

def item_complete_check(bug_item):
    assert 'whitehat' in bug_item
    assert 'status' in bug_item
    assert 'submit_time' in bug_item
    assert ('corp_response' in bug_item) or (bug_item['status'] in no_response_strs) or bug_item['bug_id'] in no_response_bug_ids
    assert 'self_threat_level' in bug_item
    assert 'bug_type' in bug_item
    assert 'bug_id' in bug_item
    assert 'reply_num' in bug_item
    assert ('corp_threat_level') in bug_item or (bug_item['status'] in no_response_strs) or bug_item['bug_id'] in no_response_bug_ids
    assert ('confirm_time') in bug_item or (bug_item['status'] in no_response_strs) or bug_item['bug_id'] in no_response_bug_ids
    assert 'corp' in bug_item
    assert 'name' in bug_item

cj = http.cookiejar.CookieJar()

#We create an opener which could be used to add cookie, user-agent, etc.

opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

opener.addheaders = [('User-agent','Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)')]

urllib.request.install_opener(opener)


urls = []

f = open("../data/bug_url_list.txt", "r")

for url in f:
    urls.append(url)

items = []

if isFromOnline:
    if isFromOnlineFailParsingOnly:
        for file in parsing_fail_files:
            strs = file.split('/')
            items.append(bug_url + strs[len(strs) - 1].split('.')[0])
    else:
        items = urls
else:
    items = reports



item_count = 0


item_count_start = 43157


exception_reports = []

insert_item_count = 0

for item in items:
    
    item_count += 1
    if item_count < item_count_start:
        continue

    print(item_count) 
    print(item)   
    
    try:

        if not isFromOnline:
            if item in parsing_fail_files:
                print("Warning: skipped one failed parsing file.")
                continue
    
        
        if isFromOnline:
            req = opener.open(item)
            soup = BeautifulSoup(req.read())
        else:
            soup = BeautifulSoup(codecs.open(item).read())
    
    
        bug_item = {}
    
        bug_id_tag = soup.find(is_bug_id)
        bug_id = bug_id_tag.string
        bug_item['bug_id'] = bug_id
        
        bug_find = bugs.find_one({'bug_id': bug_id})
        if bug_find != None:
            print("Warning: " + bug_id + " already exists.")
            continue    
        
        bug_name_tag = soup.find(is_bug_name)
        if bug_name_tag != None:
            strs = bug_name_tag.string.split("\t")
            bug_name = strs[2].strip()
        else:
            bug_name_tag = soup.find(is_bug_name_with_cloud)
            bug_name = str(bug_name_tag).split("\t")[2].strip()
        bug_item['name'] = bug_name
        
        bug_corp_tag = soup.find(is_bug_corp)
        bug_corp = bug_corp_tag['href'][corp_url_len:];
        bug_item['corp'] = bug_corp
    
        whitehat_tag = soup.find(is_whitehat)
        whitehat = whitehat_tag['href'][whitehat_url_len:];   
        bug_item['whitehat'] = whitehat
    
        submit_time_tag = soup.find(is_submit_time)
        strs = submit_time_tag.string.split("\t")
        submit_time = strs[2];
        assert submit_time != ''
        bug_item['submit_time'] = submit_time
    
        public_time_tag = soup.find(is_public_time)
        if(public_time_tag != None):
            strs = public_time_tag.string.split("\t")
            public_time = strs[2];
            assert public_time != ''
            bug_item['public_time'] = public_time
        
        confirm_time_tag = soup.find(is_confirm_time)
        if confirm_time_tag != None:
            # The following colon is in the Chinese character set
            confirm_time = confirm_time_tag.string.split("：")[1]
            assert confirm_time != ''
            bug_item['confirm_time'] = confirm_time
      
        ignore_time_tag = soup.find(is_ignore_time)
        if ignore_time_tag != None:
            # The following colon is in the Chinese character set
            ignore_time = ignore_time_tag.string.split("：")[1]
            assert ignore_time != ''
            # Since ignore time is also a kind of confirm time, we merge them together.
            bug_item['confirm_time'] = ignore_time
    
        self_threat_level_tag = soup.find(is_self_threat_level)
        if(self_threat_level_tag != None):
            strs = self_threat_level_tag.string.split("\t")
            self_threat_level = strs[2];
            assert self_threat_level != ''
            bug_item['self_threat_level'] = self_threat_level
    
        corp_threat_level_tag = soup.find(is_corp_threat_level)
        if(corp_threat_level_tag != None):
            
            strs = corp_threat_level_tag.string.split("：")
            corp_threat_level = strs[1];
            assert corp_threat_level != ''
            bug_item['corp_threat_level'] = corp_threat_level
    
        self_rank_tag = soup.find(is_self_rank)
        if(self_rank_tag != None):
            strs = self_rank_tag.string.split("\t")
            self_rank = strs[2];
            assert self_rank != ''
            bug_item['self_rank'] = int(self_rank)
    
        status_tag = soup.find(is_status)
        strs = status_tag.string.split("\t")
        status = get_longest_string(strs)[0:len(strs[17]) - 2];
        assert status != ''
        bug_item['status'] = status
    
        bug_type_tag = soup.find(is_bug_type)
        if(bug_type_tag != None):
            strs = bug_type_tag.string.split("\t")
            bug_item['bug_type'] = strs[2]
            # The follow code consider type str1/str2 as two types.
            # However, I found out that Wooyun use str1/str2 to represent on type
            # So we now abandon the following code
            #bug_type = strs[2];
            #if bug_type != '':
            #    bug_type_list = bug_type.split("/")
            #    print(bug_type_list)
            #    bug_item['bug_type'] = bug_type_list
        
        attention_num_tag = soup.find(id = 'attention_num')
        attention_num = attention_num_tag.string
        bug_item['attention_num'] = int(attention_num)
    
    
        bug_tag_list = []
    
        bug_tags = soup.find_all(is_bug_tag)
        for tag in bug_tags:
            bug_tag_list.append(tag.string)
        if len(bug_tag_list) > 0:
            bug_item["bug_tags"] = bug_tag_list
        
        
        corp_response_tag = soup.find(is_corp_response)
        if corp_response_tag != None:
            response_tag = corp_response_tag.findNext('p')
            response = response_tag.string
            assert response != ""
            bug_item["corp_response"] = response
        
        
        #Now, we try to analyze replies
        reply_whitehat_tags = soup.find_all(is_reply_whitehat)
    
        reply_list = []
    
        reply_id_list = soup.find_all(is_reply_id)
        for tag in reply_id_list:
            id_tag = tag
            while tag.next_sibling.name != 'a':
                tag = tag.next_sibling
            whitehat = tag.next_sibling.attrs['title'].split(' ')[1]
            reply_list.append({'id': id_tag.string[0:len(id_tag.string) - 1], 'whitehat': whitehat});
    
        bug_item['reply_num'] = len(reply_list)
    
        if len(reply_list) > 0:
            bug_item['reply_list'] = reply_list
    
        
        
        #print(bug_item)   
    
        item_complete_check(bug_item)
    
        #insert the bug_item into mongodb
        bugs.insert(bug_item)
        
        insert_item_count += 1    
        
        #break
        if isFromOnline:
            time.sleep(1)
    except:
        exception_reports.append(item)
        print("Exception at " + item)
        
f_exception = open("exception_reports.txt", "w")

for report in exception_reports:
    f_exception.write(report + "\n")

f_exception.close()


f.close()

print(str(insert_item_count) + " items inserted.")
