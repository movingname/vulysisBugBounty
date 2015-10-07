




file_bug_url_list = open("../data/bug_url_list.txt","r")

bug_urls = []

no_duplicate_bug_url = True

for line in file_bug_url_list:
    if line not in bug_urls:
        bug_urls.append(bug_urls)
    else:
        print("Duplicate: " + line)
        no_duplicate_bug_url = False

if no_duplicate_bug_url:
    print("No duplicate bug url found.")