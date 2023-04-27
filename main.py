import requests 
import sys 
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
from userprompt import main
from datetime import datetime 
from dateutil.relativedelta import relativedelta

contents = main()
#might be useful to destructure contents array to variables that have well-defined names so it's clear! 
domain, earliestcreated, topic = contents 
resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&q={topic}&dateRestrict={'y[' + earliestcreated + ']'}&siteSearch={domain}")
body = resp.json()
searchResults = body["items"]
for item in body["items"]:
    #get the last modified timestamp for each search item! 
    if("pagemap" in item):
        cur_pagemap = item["pagemap"]
        if("metatags" in cur_pagemap):
            metatags = cur_pagemap["metatags"]
            cur_time = None 
            #check if metatags have last_modified or date-modified timestamp! 
            if("last_modified" in metatags):
                cur_time = metatags["last_modified"]
            if("date-modified" in metatags):
                cur_time = metatags["date-modified"]
            #if there is info on cur_time, check if it meets restriction on outdatedness! 
            if cur_time: 
                print("cur_time: ", cur_time)
                if(relativedelta(datetime.now(), cur_time).years <= int(earliestcreated)):
                    print("Good")
                else:
                    print("bad")
            else:
                print("No info on last updated timestamp!")
        else:
            print("No metatags!")
    else:
        print("No pagemap key found in current search item!")






  