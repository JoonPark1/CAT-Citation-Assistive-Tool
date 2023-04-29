import requests 
import sys 
from bs4 import BeautifulSoup
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
from userprompt import main
from datetime import datetime 
import openai
import os 
from decouple import config

#read in env. variable values! 
openai.api_key = config("openai.api_key")
model_engine = config("model_engine") 
contents = main()
#might be useful to destructure contents array to variables that have well-defined names so it's clear! 
domain,topic = contents 
resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&q={topic}&siteSearch={domain}", verify=False)
body = resp.json()
searchResults = body["items"]
#array of links 
links = [] 
for item in body["items"]:
    links.append(item["link"])

#for each link, resolve it to get web html doc and parse it using beautifulSoup module! 
#for link in links: 
    #resolve link
link_resp = requests.get(links[0])
html_content = link_resp.text
#create soup instance!
soup = BeautifulSoup(html_content, "html.parser")
all_p_tags = soup.find_all("p")
# print("all_p_tags: ", all_p_tags)
p_arr = [t.string for t in all_p_tags if type(t) is not None and type(t.string) is not None]
p_arr = list(filter(lambda x: x != None, p_arr))

prompt="Please provide a summary on the following text: "
overall_p = "" 
for e in p_arr:
    overall_p += e 
prompt += overall_p[:50] 

# response = openai.Completion.create(engine=model_engine, max_tokens=1000, prompt=prompt)

# print(response)

response = openai.ChatCompletion.create(
    model = model_engine,
    messages = [
        {"role": "system", "content": "chat"},
        {"role": "user", "content": "What is " + topic},
    ],
    max_tokens = 3900
)
print(response)
# print("Here is the web info: ", p_arr)









  