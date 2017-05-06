# -*- coding: utf-8 -*-
from __future__ import print_function, division

#------------------------------------------------------------------------------
# WEBSCRAPPING - LAZADA - 1 PRODUCT PAGE - v1.0
#------------------------------------------------------------------------------
      
#------------------------------------------------------------------------------
# Initiating
#------------------------------------------------------------------------------

# Essential packages
import pandas as pd
import re
from time import time, sleep

# Other functional packages
from bs4 import BeautifulSoup, SoupStrainer # Web scrapping
import urllib2
from urllib2 import urlopen # Download link
from urlparse import urlparse # Parse URL
from datetime import datetime # Parse date time

#------------------------------------------------------------------------------
# Function to do web scrapping
#------------------------------------------------------------------------------

# Function to extract domain name from a link
def domain_extract(url):
    parsed_uri = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    return domain

# Function to open a page, try several times if the page gets stuck
def urlopen_wrapper(url, num_retry=3, delay=30):
    count_retry = 0
    while  count_retry < num_retry:
        try:
            page = urlopen(url, timeout=30)
            break # If no error, exit while loop
            
        except urllib2.URLError as e:
            print('Page load error:', e)
            print('Waiting and retrying...')
            count_retry += 1
            sleep(delay)
    
    return page

# Function to get all the news' links in a home page    
def homepage_initiate(url_homepage):

    #url_homepage = 'http://tuoitre.vn/'
    news_df = pd.DataFrame()
    
    # Try to open the page
    try:
        page = urlopen_wrapper(url_homepage)
    except:
        print('Page load failed. Webscrapping stopped.')
        return news_df # Blank data frame
        
    # Parse the page
    soup = BeautifulSoup(page, "html.parser")
    
    # Extract all news URL in the home page
    count = 0
    for a in soup.find_all('a', href=True):
        if (re.search('tuoitre.vn', domain_extract(a.get('href'))) and # Belong to the page
            re.search('/tin/', a.get('href')) and # Belong to the news group
            a.get('href')[-5:] == '.html'): # Be a news page
    
            count += 1
            news_url = a.get('href')
            news_title = a.get('title')
    
            news_row = pd.Series({'url':news_url, 'title':news_title})
            news_df = news_df.append(news_row, ignore_index=True)

    if len(news_df) != 0:
        news_df = news_df[-news_df['title'].isnull()] # Remove url without title
        news_df = news_df.drop_duplicates('url', keep='first') # Drop duplicated news
        news_df.reset_index(drop=True, inplace=True)
    
    return news_df 

# Function to scrap a news page (e.g. title, content, date, category, other links...)
def scrap_news_page(page_url, date_limit=''):
    
    #page_url = 'http://tuoitre.vn/tin/chinh-tri-xa-hoi/20161109/chu-tich-evn-noi-ve-ly-do-de-nghi-dung-du-an-dien-hat-nhan/1216399.html'
    page = urlopen_wrapper(page_url)
    soup = BeautifulSoup(page, "html.parser")
    
    # Extract news information itself
    mega_menu = soup.find(attrs={'class':'mega-menu'})
    news_category = mega_menu.ul.li.text.strip() # News category    
    
    title = soup.find(attrs={'class':'title-2'})
    news_title = title.text.strip() # News title
    
    tool_bar = soup.find(attrs={'class':'tool-bar'})
    news_date_str = tool_bar.text.strip() # News date
    news_date_str = re.sub('GMT.+', '', news_date_str).strip()
    news_date = datetime.strptime(news_date_str, '%d/%m/%Y %H:%M')
    
    # Date-time condition
    if date_limit != '':
        date_limit = datetime.strptime(date_limit, '%d/%m/%Y %H:%M')
        if news_date < date_limit: # News date in the past
            news_body = pd.Series({'url':page_url,
                                   'domain':domain_extract(page_url),
                                   'status':'out date'})
            related_news_df = pd.DataFrame()
            return news_body, related_news_df
    
    txt_head = soup.find(attrs={'class':'txt-head'})
    news_text_head = txt_head.text.strip() # News head text (summary)
    
    content = soup.find(attrs={'class':'fck '})
    news_content = '' # News content
    for p in content.find_all('p'):
        news_content = news_content + '\n' + p.text.strip()
    news_content = news_content.strip()
        
    lower_bar = soup.find(attrs={'class':'wrapper-qt'})
    news_reporter = lower_bar.text.strip() # News reporter's name
    
    news_body = pd.Series({'category':news_category,
                           'title':news_title,
                           'date':news_date,
                           'summary':news_text_head,
                           'content':news_content,
                           'author':news_reporter,
                           'url':page_url,
                           'domain':domain_extract(page_url),
                           'status':'done'})
    
    # Extract all other news url
    related_news_df = pd.DataFrame()
        
    count = 0
    for a in soup.find_all('a', href=True):
        if (re.search('tuoitre.vn', domain_extract(a.get('href'))) and
            re.search('/tin/', a.get('href')) and
            a.get('href')[-5:] == '.html'): # News page
            
            count += 1
            news_url = a.get('href')
            news_title = a.get('title')
    
            news_row = pd.Series({'url':news_url, 'title':news_title})
            related_news_df = related_news_df.append(news_row, ignore_index=True)

    if len(related_news_df) != 0:
        related_news_df = related_news_df[-related_news_df['title'].isnull()] # Remove url without title
        related_news_df = related_news_df.drop_duplicates('url', keep='first') # Drop duplicated news
        related_news_df.reset_index(drop=True, inplace=True)
    
    return news_body, related_news_df

# Just a wrapper, in case the page is not in the right format       
def scrap_news_page_wrapper(page_url, date_limit=''):
    try:
        news_body, related_news_df = scrap_news_page(page_url, date_limit)
    except:
        news_body = pd.Series({'url':page_url,
                               'domain':domain_extract(page_url),
                               'status':'failed'})
        related_news_df = pd.DataFrame()
    return news_body, related_news_df

# Function to scrap a list of multiple urls    
def scrap_url_list(url_df, date_limit=''):
    
    news_list_df = pd.DataFrame()
    related_url_list_df = pd.DataFrame()
    
    count = 0
    for idx, row in url_df.iterrows():
        
        count += 1
        print(count, '/', len(url_df))
        print(row['title'])
        print(row['url'])
        
        news_body, related_news_df = scrap_news_page_wrapper(row['url'], date_limit)
        print(news_body['status'])
        
        news_list_df = news_list_df.append(news_body, ignore_index=True)
        related_url_list_df = related_url_list_df.append(related_news_df, ignore_index=True)

    if len(related_url_list_df) != 0:
        related_url_list_df = related_url_list_df.drop_duplicates('url', keep='first') # Drop duplicated news
        related_url_list_df.reset_index(drop=True, inplace=True)
    
    return news_list_df, related_url_list_df    
   
#------------------------------------------------------------------------------
# MAIN: Web scrapping
#------------------------------------------------------------------------------

# Scrapping homepage to get initial news' links
homepage_news_df = homepage_initiate('http://tuoitre.vn/')

# Scrapping news pages until meet stop conditions
all_url = homepage_news_df # Unique URL list to compare
next_urls = all_url # Initiate URL to scrap

count = 0

while True:
    # Scrap URL list
    news_list_df, related_news_df = scrap_url_list(next_urls, date_limit='01/11/2016 00:00')
    
    # Stop conditions
    count += len(next_urls)
    if count == 10000: break
    
    # Extract new unique URLs to continue scrap
    if len(related_news_df) != 0:
        unique_new_url = related_news_df[-related_news_df['url'].isin(all_url['url'])]
        all_url = all_url.append(unique_new_url) # Update all URLs list
        next_urls = unique_new_url # Continue scrap new URLs
    else: break
    
#------------------------------------------------------------------------------
# Scrapping a specific news group
#------------------------------------------------------------------------------

page_url = 'http://tuoitre.vn/tin/chinh-tri-xa-hoi'

news_content = pd.DataFrame()
news_urls = pd.DataFrame()

# Try to open the page
try:
    page = urlopen_wrapper(page_url)
except:
    print('Page load failed. Webscrapping stopped.')
    
# Parse the page
soup = BeautifulSoup(page, "html.parser")

content = soup.find('section', attrs={'class':'content'})
left_side = content.find('div', attrs={'class':'left-side'})

# Add the 1st top news
top_news_1 = left_side.find('div', attrs={'class':'block-feature'})
news_url = pd.Series({'title':top_news_1.h1.text.strip(),
                      'url':top_news_1.h1.a.get('href')})
news_urls = news_urls.append(news_url, ignore_index=True)

# Add the 2nd, 3rd, 4th top news
list_news = content.find('ul', attrs={'class':'list-news'})
for li in list_news.find_all('li'):
    news_url = pd.Series({'title':li.h4.text.strip(),
                          'url':li.h4.a.get('href')})
    news_urls = news_urls.append(news_url, ignore_index=True)
    
# Add 1st latest news
latest_news = content.find('div', attrs={'class':'newhot_most_content'})

latest_news_1 = latest_news.find('div', attrs={'class':'block-left block-top'})
news_url = pd.Series({'title':latest_news_1.h3.text.strip(),
                      'url':latest_news_1.h3.a.get('href')})
news_date = datetime.strptime(latest_news_1.span.text.strip(), '%d/%m/%Y %H:%M')
news_urls = news_urls.append(news_url, ignore_index=True)

# Add other latest news
for div in latest_news.find_all('div', attrs={'class':'block-left'}):
    news_url = pd.Series({'title':div.h3.text.strip(),
                          'url':div.h3.a.get('href')})
    news_date = datetime.strptime(div.span.text.strip(), '%d/%m/%Y %H:%M')
    print(news_date)
    news_urls = news_urls.append(news_url, ignore_index=True)


# Extract all news URL in the home page
count = 0
for a in soup.find_all('a', href=True):
    if (re.search('tuoitre.vn', domain_extract(a.get('href'))) and # Belong to the page
        re.search('/tin/', a.get('href')) and # Belong to the news group
        a.get('href')[-5:] == '.html'): # Be a news page

        count += 1
        news_url = a.get('href')
        news_title = a.get('title')

        news_row = pd.Series({'url':news_url, 'title':news_title})
        news_df = news_df.append(news_row, ignore_index=True)

if len(news_df) != 0:
    news_df = news_df[-news_df['title'].isnull()] # Remove url without title
    news_df = news_df.drop_duplicates('url', keep='first') # Drop duplicated news
    news_df.reset_index(drop=True, inplace=True)