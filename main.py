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

def generate_response(in_prompt, domain):
    #read in env. variable values! 
    openai.api_key = config("openai.api_key")
    model_engine = config("model_engine") 
    # contents = main()
    
    #If user don't provide domain, default to .com! 
    if not domain:
        domain = ".com"
        
    #might be useful to destructure contents array to variables that have well-defined names so it's clear! 
    # domain,topic = contents 
    topic=in_prompt
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
    output_string = "" 
    while True:
        cur = random.randint(0, length-1)
        link = links[cur]
        if counter == 3:
            break 
        if link not in considered: 
            print("link: ", link)
            link_resp = requests.get(link)
            html_content = link_resp.text
            #print("html_content: ", html_content)
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
                max_tokens = 2000
            )
            #output response
            print("Start!\n")
            print(response['choices'][0]['message']['content'])
            print("End!\n")
            considered.add(link)
            counter += 1 
            output_string += (response['choices'][0]['message']['content']) 
    return output_string

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content= request.form['content']
        domain = request.form['domain']
        print("domain: ", domain)
        prompt_out = generate_response(task_content, domain)
        return render_template('index.html',fin_out=prompt_out)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)