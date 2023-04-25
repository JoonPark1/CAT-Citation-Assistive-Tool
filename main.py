import requests 
from userprompt import main
from datetime import datetime 
from dateutil.relativedelta import relativedelta

contents = main()
#print(contents)

resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&q={contents[2]}&dateRestrict={contents[1]}")
body = resp.json()
for item in body["items"]:
    cur_time = item["metadata"]["article:modified_time"]
    if(relativedelta(datetime.now(), cur_time).years()) <= contents[1]:
        print("Good")
    else:
        print("bad")
# for item in body:
#     print(item.dateRestrict)
#print("body: ", body)

  