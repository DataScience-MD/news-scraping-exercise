# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 15:23:39 2019

@author: Dr. Mark M. Bailey | National Intelligence University
"""

#News Scrape

#Import libraries
import selenium.webdriver as webdriver
import time
from bs4 import BeautifulSoup
import requests
from lxml import html
import pickle
import os

#Define functions
"""
GENERAL FUNCTIONS
"""

#save object to pickle
def save_pickle(output_path, pickle_object, file_name):
    output_name = os.path.join(output_path, file_name + '.pkl')
    with open(output_name, 'wb') as pkl_object:
        pickle.dump(pickle_object, pkl_object)

#open pickle file
def open_pickle(pickle_path):
    with open(pickle_path, 'rb') as pickle_file:
        object_name = pickle.load(pickle_file)
    return object_name

#Get urls from news object
def open_file(news_object_path):
    news_object_file = os.path.join(news_object_path, 'news_dump_object.pkl')
    old_news = open_pickle(news_object_file)
    old_url_list = []
    for item in old_news:
        url = item['url']
        old_url_list.append(url)
    old_url_set = set(old_url_list)
    return old_news, old_url_set
    
#url check
def url_check(old_url_set, url):
    url_set = set([url])
    test_set = old_url_set & url_set
    if len(test_set) == 0:
        check = False
    else:
        check = True
    return check

#Concat outut lists
def concat_lists(out_lists):
    output = []
    for outlist in out_lists:
        output = output + outlist
    return output

"""
GET LINKS FROM HTML
"""

#get HTML with page scroll
def get_html_scroll(url):
    browser = webdriver.Firefox()
    browser.get(url)
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(4)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            time.sleep(4)
            match=True
    post_elms = browser.page_source
    return post_elms

#get HTML file
def get_html(url):
    page = requests.get(url)
    html_out = html.fromstring(page.content)
    text = page.text
    return html_out, text

#get soup
def get_soup(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup

#get links
def get_soup_links(soup):
    links = []
    for link in soup.find_all('a'):
        out_link = link.get('href')
        links.append(out_link)
    return links

"""
REUTERS FUNCTIONS
"""
#get article links
def get_articles_reuters(links, old_url_set):
    articles = []
    for link in links:
        try:
            if 'article' in link:
                if url_check(old_url_set, link) == False:
                    articles.append(link)
        except:
            continue
    return articles

#get article html
def get_html_reuters(articles):
    soup_list = []
    for article in articles:
        _, text = get_html(article)
        soup = get_soup(text)
        soup_list.append(soup)
    return soup_list

#date formatter
def format_date(date):
    date_dict = {'January':'1','February':'2','March':'3','April':'4','May':'5','June':'6','July':'7','August':'8','September':'9','October':'10','November':'11','December':'12'}
    split_date = date.split(' ')
    year = split_date[2]
    day_list = split_date[1].split(',')[0]
    day = day_list
    month = date_dict[split_date[0]]
    out_date = year + '-' + month + '-' + day
    return out_date

#get elements
def get_reuters_elements(soup_list, articles):
    out_list = []
    i = 0
    for article in soup_list:
        link = articles[i]
        i += 1
        try:
            article_body = article.find_all('div', {'class': 'StandardArticleBody_body'})
            article_headline = article.find_all('h1', {'class': 'ArticleHeader_headline'})
            article_date = article.find_all('div', {'class': 'ArticleHeader_date'})
            try:
                date_time = article_date[0].text.split(' / ')
                date_in = date_time[0]
                date = format_date(date_in)
                a_time = date_time[1][1:]
            except:
                date = article_date[0].text
                time = article_date[0].text
            headline = article_headline[0].text
            article_p = []
            for item in article_body:
                p_list = item.find_all('p')
                for p in p_list:
                    article_p.append(p.text)
            out_text = ' '.join(article_p)
            out_dict = dict([('date',date),('time',a_time),('source','www.reuters.com'),('Title',headline),('Text',out_text),('url',link)])
            out_list.append(out_dict)
        except:
            print('Unable to decode...skipping article...')
            continue
    return out_list

#Execute Reuters script
def reuters(old_url_set):
    print('Getting Reuters articles...')
    url = 'https://www.reuters.com/theWire'
    post_elms = get_html_scroll(url)
    soup = get_soup(post_elms)
    links = get_soup_links(soup)
    articles = get_articles_reuters(links, old_url_set)
    soup_list = get_html_reuters(articles)
    reuters_list = get_reuters_elements(soup_list, articles)
    return reuters_list

"""
MAIN SCRIPT
"""
def main():
    news_object_path = os.getcwd()
    output_path = os.getcwd()
    old_news, old_url_set = open_file(news_object_path)
    reuters_list = reuters(old_url_set)
    out_lists = [old_news, reuters_list]
    output_reuters = concat_lists(out_lists)
    print('Saving news object...')
    save_pickle(output_path, output_reuters, 'news_dump_object')
    return output_reuters


"""
EXECUTE SCRIPT
"""
if __name__ == '__main__':
    output_reuters = main()
