import requests 
import sys 
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
from userprompt import main
from datetime import datetime 
from dateutil.relativedelta import relativedelta

contents = main()
#might be useful to destructure contents array to variables that have well-defined names so it's clear! 
domain,topic = contents 
resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&q={topic}&siteSearch={domain}", verify=False)
body = resp.json()
searchResults = body["items"]
for item in body["items"]:
    print("item: ", item)






  