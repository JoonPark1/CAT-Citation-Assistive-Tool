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

def generate_response(in_prompt):
    #read in env. variable values! 
    openai.api_key = config("openai.api_key")
    model_engine = config("model_engine") 
    # contents = main()

    #might be useful to destructure contents array to variables that have well-defined names so it's clear! 
    # domain,topic = contents 
    domain=".org"
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
    link_resp = requests.get(links[0])
    html_content = link_resp.text

    #define parsing functions
    # for a in soup.findAll('a', href=True):
    #     a.extract()


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

    formatted=text_from_html(html_content)
    formatted = formatted[:5000]

    # all_p_tags = soup.find_all("p")
    # p_arr = [t.string for t in all_p_tags if type(t) is not None and type(t.string) is not None]
    # p_arr = list(filter(lambda x: x != None, p_arr))

    #generate prompt
    # prompt="Please provide a summary on the following text: "
    # overall_p = ""
    # for e in p_arr:
    #     overall_p += e
    # prompt += overall_p[:50]
    prompt = "The following text is all of the text on a website including things that are not important. Please summarize the most crucial and core parts of this content: "
    prompt += formatted

    #retrieve response
    # response = openai.Completion.create(engine=model_engine, max_tokens=1000, prompt=prompt)
    response = openai.ChatCompletion.create(
        model = model_engine,
        messages = [
            {"role": "system", "content": "chat"},
            {"role": "user", "content": prompt},
        ],
        max_tokens = 2000
    )

    #output response
    return response['choices'][0]['message']['content']
    # print("Here is the web info: ", p_arr)

app = Flask(__name__)
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content= request.form['content']
        prompt_out = generate_response(task_content)
        return render_template('index.html',fin_out=prompt_out)
    else:
        return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)










    