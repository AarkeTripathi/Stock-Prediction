from transformers import PegasusTokenizer, PegasusForConditionalGeneration, pipeline
from bs4 import BeautifulSoup
import requests
import pandas as pd
import yahoo_fin.stock_info as yf
import re

model_name='human-centered-summarization/financial-summarization-pegasus'
tokenizer=PegasusTokenizer.from_pretrained(model_name)
model=PegasusForConditionalGeneration.from_pretrained(model_name)             
sentiment=pipeline('sentiment-analysis')

data_fr = pd.DataFrame( yf.tickers_sp500() )
sym = set( symbol for symbol in data_fr[0].values.tolist() )
sym=list(sym)

temp_lst=['TSLA','GOOG','ADE']

def stock_info(ticker):
    url=f"https://www.google.com/seach?q=yahoo+finance+{ticker}&tbm=nws"
    r=requests.get(url)
    soup=BeautifulSoup(r.text, 'html.parser')
    anchor_tags=soup.find_all('a')
    hrefs=[link['href'] for link in anchor_tags]
    return hrefs



def remove_rubbish(urls, rubbish):
    lst=[]
    for url in urls:
        if 'https://' in url and not any(exclude_word in url for exclude_word in rubbish):
            res = re.findall(r'(https?://\S+)', url)[0].split('&')[0]
            lst.append(res)
    return list(set(lst))



def scrape_and_process(urls):
    ARTICLES = []
    for url in urls: 
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = [paragraph.text for paragraph in paragraphs]
        words = ' '.join(text).split(' ')[:350]
        ARTICLE = ' '.join(words)
        ARTICLES.append(ARTICLE)
    return ARTICLES



def summarization(articles):
    summaries = []
    for article in articles:
        input_ids = tokenizer.encode(article, return_tensors='pt')
        output = model.generate(input_ids, max_length=55, num_beams=5, early_stopping=True)
        summary = tokenizer.decode(output[0], skip_special_tokens=True)
        summaries.append(summary)
    return summaries



def search_stock():
    urls={ticker:stock_info(ticker) for ticker in sym}
    rubbish=['maps','policies','preferences','accounts','support']
    cleaned_urls = {ticker:remove_rubbish(urls[ticker], rubbish) for ticker in sym}
    articles = {ticker:scrape_and_process(cleaned_urls[ticker]) for ticker in sym}
    summarised_articles={ticker:summarization(articles[ticker]) for ticker in sym}
    scores = {ticker:sentiment(summarised_articles[ticker]) for ticker in sym}
    dic={}
    for ticker in sym:
        counter=0
        for i in scores[ticker]:
            if(i['label']=='POSITIVE'):
                counter=counter+1
        num=len(scores[ticker])
        if(counter>=num*0.5):
            dic[ticker]='POSITIVE'
        else:
            dic[ticker]='NEGATIVE'
    return dic



