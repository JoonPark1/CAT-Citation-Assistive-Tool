import random
import requests 
import sys 
from bs4 import BeautifulSoup
from bs4.element import Comment
import urllib.request
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.9/lib/python3.9/site-packages")
from userprompt import main
from datetime import datetime 
import openai
import os 
from decouple import config
from flask import Flask, render_template, url_for, request, redirect
cert_path = "./root-chr.cer"
os.environ['REQUESTS_CA_BUNDLE'] = cert_path 
#create soup instance!
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True

def text_from_html(body):
    soup = BeautifulSoup(body, 'html.parser')
    for a in soup.findAll('a', href=True):
        a.extract()
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)  
    return " ".join(t.strip() for t in visible_texts)



def generate_response(in_prompt, domain, earliest_date, latest_date):
    #read in env. variable values! 
    openai.api_key = config("openai.api_key")
    model_engine = config("model_engine") 
    #If user don't provide domain, default to .com! 
    if not domain:
        domain = ".com"
        
    #might be useful to destructure contents array to variables that have well-defined names so it's clear! 
    # domain,topic = contents 
    topic=in_prompt
    print("earliest_date_text: ", earliest_date)
    print("latest_date_text: ", latest_date) 
    resp = None 
    if earliest_date and latest_date:
        print("get to url with both dates called!")
        phrase = f"Before:{earliest_date} After:{latest_date}" 
        print("phrase: ", phrase)
        resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&fields=items(link)&q={topic}&dateRestrict={phrase}&siteSearch={domain}", verify=False)
    elif earliest_date: 
        print("get to url with jsut earliest date called!")
        phrase = f"Before:{earliest_date}"
        print("phrase: ", phrase)
        resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&fields=items(link)&q={topic}&dateRestrict={phrase}&siteSearch={domain}", verify=False)
    elif latest_date:
        print("get to url with just latest date called!")
        phrase = f"After:{latest_date}:" 
        print("phrase: ", phrase)
        resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&fields=items(link)&q={topic}&dateRestrict={phrase}&siteSearch={domain}", verify=False)
        print(resp.headers["Last Modified"])
    else: 
        print("normal get url called!")
        resp = requests.get(f"https://www.googleapis.com/customsearch/v1?key=AIzaSyBcD-oHPwnM6W7MpWSp2p1BHO_4ppkKUuE&cx=d44d7375edf8c41be&fields=items(link)&q={topic}&siteSearch={domain}", verify=False)
    body = resp.json()
    searchResults = body["items"]

    #array of links 
    links = [] 
    for item in body["items"]:
        links.append(item["link"])

    #for each link, resolve it to get web html doc and parse it using beautifulSoup module! 
    #for link in links: 
        #resolve link
    considered = set() 
    length = len(links)
    counter = 0 
    links_list = []
    while True:
        cur = random.randint(0, length-1)
        link = links[cur]
        if counter == 3:
            break 
        if link not in considered: 
            USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
            headers = {"user-agent": USER_AGENT}
            link_resp = requests.get(link, headers = headers, verify=False)
            html_content = link_resp.text
            formatted= text_from_html(html_content)
            formatted = formatted[:5000]
            prompt = "The following text is all of the text on a website including things that are not important. Please summarize the most crucial and core parts of this content: "
            prompt += formatted
            response = openai.ChatCompletion.create(
                model = model_engine,
                messages = [
                    {"role": "system", "content": "chat"},
                    {"role": "user", "content": prompt},
                ],
                max_tokens = 1950
            )
            considered.add(link)
            counter += 1 
            links_list.append([link, response['choices'][0]['message']['content']])

            print("earliest_date: ", earliest_date)
            print("latest_date: ", latest_date)
    return links_list

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content= request.form['content']
        domain = request.form['domain']
        earliest_date = request.form['earliest_date_text'] 
        latest_date = request.form['latest_date_text'] 
        array = generate_response(task_content, domain, earliest_date, latest_date)
        return render_template('index.html', link1 = array[0][0], link1_text=array[0][1], link2 = array[1][0], link2_text = array[1][1], 
                               link3 = array[2][0], link3_text = array[2][1])
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(port=5001, debug=True)