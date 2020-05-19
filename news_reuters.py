# -*- coding: utf-8 -*-
"""
Created on Sat Jul 13 15:23:39 2019

@author: Dr. Mark M. Bailey | National Intelligence 
# Changelog 18 May 2020 by team Bad Ozone Grasshoppers
- 1. main() updated to take two options "browser_agent" and "news_dump_filename"
  -- 1.1. browser agents supported are 'Firefox' and 'Chrome'
  -- 1.2. filename should be passed in "[filename].json" format

- 2. Updated to use pandas to read and save JSON files instead of pickle files 
     This was done to reduce code complexity and increase security (below are updates)
  -- 2.1. save_pickle() replaced with pd.DataFrame.to_json()
  -- 2.2. open_pickle() replaced with pd.DataFrame.read_json()
  -- 2.3. concat_lists() replaced with pd.concat()
  
- 3. Updated get_soup_links() function to remove duplicate links from list prior to returning list
"""

# News Scrape

# Import libraries
import selenium.webdriver as webdriver
import time
import requests
import pandas as pd
import os
import urllib.request
from urllib.parse import urlparse
import zipfile
import platform
import base64
# import pickle # no longer needed in json functions replaced pickle
# import json # no longer needed pandas library simplified codebase

# Import methods
from selenium.webdriver.chrome.options import Options
from lxml import html
from bs4 import BeautifulSoup


# Define functions
"""
GENERAL FUNCTIONS
"""


# save object to JSON
# def save_json(output_path, json_object, file_name):
#    output_name = os.path.join(output_path, file_name + '.json')
#    with open(output_name, 'w') as json_file:
#        json.dump(json_object, json_file)

# open JSON file
# def open_json(json_path):
#    with open(json_path, 'rb') as json_file:
#        object_name = json.load(json_file)
#    return object_name

# save object to pickle
# Deprecated replaced by save_json function
# def save_pickle(output_path, pickle_object, file_name):
#    output_name = os.path.join(output_path, file_name + '.pkl')
#    with open(output_name, 'wb') as pkl_object:
#        pickle.dump(pickle_object, pkl_object)

# open pickle file
# Deprecated by open_json function
# def open_pickle(pickle_path):
#    with open(pickle_path, 'rb') as pickle_file:
#        object_name = pickle.load(pickle_file)
#    return object_name

# Get urls from news object
# updated to use pandas dataframe to parse the URLs and store the set
def open_file(news_object_path, news_object_file):
    news_object_file = os.path.join(news_object_path, news_object_file)
    old_news_df = pd.read_json(news_object_file)
    old_url_set = set(old_news_df['url'].values)
    return old_news_df, old_url_set


# url check
def url_check(old_url_set, url):
    scheme = urlparse(url) # parses the url into parts
    url_set = {url}
    test_set = old_url_set & url_set
    if len(test_set) == 0 and scheme.scheme: # Fixed parse error added scheme validation, will not process urls without scheme i.e. url missin 'https://'
        check = False
    else:
        check = True
    return check


# Concat outut lists
# Deprecated now using pandas concat function.
# def concat_lists(out_lists):
#    output = []
#    for outlist in out_lists:
#        output = output + outlist
#    return output

"""
GET LINKS FROM HTML
"""


# get HTML with page scroll
# Function updated to allow user to define the browser agent
# Browser flag allows the userpa to define the type of browser used by selenium
# Code supports Firefox and Chrome, default is Firefox if no browser agent is specified
def get_html_scroll(url, browser_agent="Firefox"):
    # calls the webdriver based on the user's selection
    if browser_agent == "Firefox":
        browser = webdriver.Firefox()
    elif browser_agent == "Chrome":
        chrome_options = Options() # Using Options() to fix deprecation warning of manual options declarations
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        browser = webdriver.Chrome('chromedriver', options=chrome_options) # Using 'options=' to fix deprecation warning
    # else:
    # else section intentionally empty and reserved for future use

    browser.get(url)
    lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);" +
                                       "var lenOfPage=document.body.scrollHeight;" +
                                       "return lenOfPage;")
    match = False
    while (match == False):
        lastCount = lenOfPage
        time.sleep(4)
        lenOfPage = browser.execute_script("window.scrollTo(0, document.body.scrollHeight);" +
                                           "var lenOfPage=document.body.scrollHeight;" +
                                           "return lenOfPage;")
        if lastCount == lenOfPage:
            time.sleep(4)
            match = True
    post_elms = browser.page_source
    return post_elms


# get HTML file
def get_html(url):
    page = requests.get(url)
    html_out = html.fromstring(page.content)
    text = page.text
    return html_out, text


# get soup
def get_soup(html_string):
    soup = BeautifulSoup(html_string, 'html.parser')
    return soup


# get links
def get_soup_links(soup):
    links = []
    for link in soup.find_all('a'):
        out_link = link.get('href')
        links.append(out_link)
    # Remove duplicates from links
    # Below line removes all duplicate links prior to passing the list of links back
    # This is accomplished by converting the list of links into a dictionary and then back to a list
    links = list(dict.fromkeys(links))
    return links


"""
REUTERS FUNCTIONS
"""


# get article links
def get_articles_reuters(links, old_url_set):
    articles = []
    for link in links:
        try:
            if 'article' in link:
                if not url_check(old_url_set, link):
                    articles.append(link)
        except:
            continue
    return articles


# get article html
def get_html_reuters(articles):
    soup_list = []
    for article in articles:
        _, text = get_html(article)
        soup = get_soup(text)
        soup_list.append(soup)
    return soup_list


# date formatter
def format_date(date):
    date_dict = {'January': '1', 'February': '2', 'March': '3', 'April': '4', 'May': '5', 'June': '6', 'July': '7',
                 'August': '8', 'September': '9', 'October': '10', 'November': '11', 'December': '12'}
    split_date = date.split(' ')
    year = split_date[2]
    day_list = split_date[1].split(',')[0]
    day = day_list
    month = date_dict[split_date[0]]
    out_date = year + '-' + month + '-' + day
    return out_date


# get elements
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
            out_dict = dict([('date', date), ('time', a_time), ('source', 'www.reuters.com'), ('Title', headline),
                             ('Text', out_text), ('url', link)])
            out_list.append(out_dict)
        except:
            print('Unable to decode...skipping article...')
            continue
    return out_list


# Execute Reuters script
def reuters(old_url_set, browser_agent):
    print('Getting Reuters articles...')
    url = 'https://www.reuters.com/theWire'
    post_elms = get_html_scroll(url, browser_agent)
    soup = get_soup(post_elms)
    links = get_soup_links(soup)
    articles = get_articles_reuters(links, old_url_set)
    soup_list = get_html_reuters(articles)
    reuters_list = get_reuters_elements(soup_list, articles)
    return reuters_list


# Get Chrome
# Adds local support for chrome driver if not found. function in OS aware, and fetches the appropiate version of
# chrome driver for the OS, extracts the zip, places the executable in the current working directory. This is the
# first checked PATH option for execution flow, then /bin, then /sbin, etc. Local placement allows for simpler
# envirment set-up, and removes the requirement to force a non standard PATH variable into sys.
def check_chrome():
    os_platform = platform.system()

    try:
        if os_platform == 'Windows':
            open('chromedriver.exe')
        else:
            open('chromedriver')
    except Exception:
        dl_url = ''
        print("Chrome Driver not found...installing locally...")

        if os_platform == 'Windows':
            dl_url = 'https://chromedriver.storage.googleapis.com/81.0.4044.138/chromedriver_win32.zip'
        else:
            dl_url = 'https://chromedriver.storage.googleapis.com/81.0.4044.138/chromedriver_linux64.zip'

        with urllib.request.urlopen(dl_url) as dl_file:
            with open('chromedriver.zip', 'wb') as out_file:
                out_file.write(dl_file.read())
                out_file.close()
        with zipfile.ZipFile('chromedriver.zip', 'r') as zip_file:
            zip_file.extractall()
            zip_file.close()
        os.remove('chromedriver.zip')
        pass

# Useless but fun
def banner():
    print(base64.b64decode("PT09PT09PT09PT09PT09PT09PT09PT09PT09PT09CnwgICBCYWQgT3pvbmUgR3" +
                           "Jhc3Nob3BwZXJzICAgfAo9PT09PT09PT09PT09PT09PT09PT09PT09PT09PT0=").decode('utf8'))

# Cleanup of temporary files
def cleanup():
    if open('chromedriver.exe'):
        os.remove('chromedriver.exe')
    elif open('chromedriver'):
        os.remove('chromedriver')
    elif open('geckodriver.log'):
        os.remove('geckodriver.log')
    return


"""python
MAIN SCRIPT
Updated function to allow user to specify a browser agent and news_dump_object filename
If not specified the code will default to a browser agent of Firefox and filename of news_dump_object.json
"""


def main(browser_agent="Chrome", news_object_file='news_dump_object.json'):
    banner()
    # Check if the requested browser agent is Firefox or Chrome
    # If no agent is passed code will defualt to Firefox
    if browser_agent == "Chrome" or browser_agent == "Firefox":
        print("Executing using", browser_agent, "webdriver")
        if browser_agent == "Chrome":
            check_chrome()
    else:
        print(browser_agent, " is not a recognized browser agent, please use 'Firefox' or 'Chrome'")
        exit(1)
    news_object_path = os.getcwd()
    output_path = os.getcwd()
    # updated below line of code to allow user to specify a news_object_filename
    old_news_df, old_url_set = open_file(news_object_path, news_object_file) # *** What if this is first run and there is no json? ***
    reuters_list_df = pd.DataFrame(reuters(old_url_set, browser_agent))
    # Updated to use pandas concat function
    output_reuters_df = pd.concat([old_news_df, reuters_list_df], ignore_index=True)
    print('Saving news object...')
    output_file = os.path.join(output_path, news_object_file)
    # Save output to JSON file using pandas
    output_reuters_df.to_json(path_or_buf=output_file)
    output_reuters = output_reuters_df.to_json()
    cleanup()
    return output_reuters


"""
EXECUTE SCRIPT
"""
if __name__ == '__main__':
    output_reuters = main()
