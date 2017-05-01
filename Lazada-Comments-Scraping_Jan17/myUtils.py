# -*- coding: utf-8 -*-
from __future__ import print_function, division

#------------------------------------------------------------------------------
# WEBSCRAPPING - LAZADA - MY FUNCTIONS - v1.0
#------------------------------------------------------------------------------
      
#------------------------------------------------------------------------------
# Initiating
#------------------------------------------------------------------------------

import os
os.chdir('D:\\Userfiles\\mphan\\Desktop\\Lazada')

# Essential packages
import pandas as pd
import re
from time import time, sleep

# Other functional packages
from bs4 import BeautifulSoup # Web scrapping
import urllib2
from urllib2 import urlopen # Download link
from urlparse import urlparse # Parse URL
from datetime import datetime # Parse date time

from selenium import webdriver

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
            print('Page load sucessful!')
            break # If no error, exit while loop
            
        except urllib2.URLError as e:
            print('Page load error:', e)
            print('Waiting and retrying...')
            count_retry += 1
            sleep(delay)
    
    return page

# Function to simulate a click, try several times if cannot click
def click_wrapper(object_click, num_retry=5, delay=5):    
    count_retry = 0
    while  count_retry < num_retry:
        try:
            object_click.click()
            print('Click successful!')
            return True
            
        except:
            print('Click failed. Retrying...')
            count_retry += 1
            sleep(delay)
    
    return False
       
# Function to scrap a single product page, return product ratings, commments, etc.
def scrap_product_reviews(product_url):
    
    #page = urlopen_wrapper(product_url)
    #soup = BeautifulSoup(page, "html.parser")
    
    driver = webdriver.Chrome() # Simulate web click
    driver.get(product_url)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    
    # Extract product name
    product_name_block = soup.find('h1', attrs={'id':'prod_title'})
    product_name = product_name_block.text.strip()
    
    # Extract product overal ratings
    try:
        totalRating_block = soup.find('div', attrs={'class':'ratingBarTotal'})
        totalRating_str = totalRating_block.next.next.next.next.next.next.next.next.next.next.next_sibling.next.get('style').split(' ')[1].strip('%')
        totalRating = float(totalRating_str)/100*5 # Over 5
    except:
        totalRating = None
    
    # Extract product ratings details
    finish = False # Loop until get all review
    customer_reviews_list = [] # List to save reviews information
    
    while finish != True:
        
        # Scroll to review section
        element = driver.find_element_by_xpath('//*[@id="product-reviews-wrapper"]')
        driver.execute_script("return arguments[0].scrollIntoView();", element)
    
        # Find the whole review block in the page
        allReviews_block = soup.find('div', attrs={'class':'ratRev_section',
                                                   'id':'reviewslist'})
        if allReviews_block is None: break # Product has no reviews
        review_block_list = allReviews_block.findAll('li', attrs={'class':'ratRev_reviewListRow'})
        
        for review_block in review_block_list:
            
            # Rating
            rating_block = review_block.find('div', attrs={'class':'product-card__rating__stars'})
            rating_str = rating_block.next.next.next_sibling.next.get('style').split(' ')[1].strip('%')
            rating = float(rating_str)/100*5 # Over 5
            
            # Review title
            review_tilte_block = review_block.find('span', attrs={'class':'ratRev_revTitle'})
            review_title = review_tilte_block.text.strip()
            
            # Review date
            review_date_block = review_block.find('span', attrs={'class':'ratRev_revDate align-right'})
            review_date = review_date_block.text.strip()
            
            # Review name
            review_name_block = review_block.find('span', attrs={'class':'ratRev-revNickname'})
            review_name = review_name_block.text.strip()
            
            # Review content
            review_content_block = review_block.find('div', attrs={'class':'ratRev_revDetail'})
            review_content = review_content_block.text.strip()
            
            customer_reviews_list.append([review_title, review_name, review_date, rating, review_content])
        
        # Find next button and click
        try:
            next_button = driver.find_elements_by_xpath('//*[@id="reviewslist"]/div[3]/ul/li')[-1]
        except:
            next_button = None
            
        if next_button != None and next_button.text == '>' and click_wrapper(next_button):
            sleep(5) # Wait for page to load
            soup = BeautifulSoup(driver.page_source, "html.parser") # Get new page content
            finish = False
        else:
            finish = True

    df = pd.DataFrame(customer_reviews_list, columns=['review_title', 'review_name', 'review_date', 'rating', 'review_content'])
    df['product_name'] = product_name
    df['totalRating'] = totalRating
    df['url'] = product_url
    
    driver.quit()
    
    return df
    
# Function to scrap a single product page, return product ratings, commments, etc.
def scrap_product_links(category_url):
    
    page = urlopen_wrapper(category_url)
    soup = BeautifulSoup(page, "html.parser")
    
    # Find product grid
    product_grid_block = soup.find('div', attrs={'class':'component component-product_list product_list grid toclear'})
    product_card_list = product_grid_block.find_all('div', attrs={'class':'product-card'})

    finish = False
    product_list = []
    page_count = 0
    
    while finish != True:
        
        page_count += 1
        print('Page', page_count)
        
        # Get all product information in the current page
        for product_card in product_card_list:
            
            # Get product url
            product_url = product_card.next.next['href']
            
            # Get product name
            product_description_block = product_card.find('div', attrs={'class':'product-card__description'})
            product_name = product_description_block.next.next.text.strip()
            
            product_list.append([product_name, product_url])

        # Find next button and click     
        next_button = soup.find('a', attrs={'class':'c-paging__next-link','title':'next page'})
        if next_button != None:
            next_page = next_button['href'] # Next page url
            page = urlopen_wrapper(next_page)
            soup = BeautifulSoup(page, "html.parser") # Get new page content
            finish = False
        else:
            finish = True

    df = pd.DataFrame(product_list, columns=['product_name', 'product_url'])
    
    return df
               
#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

# Product: iPhone 7
product_url = 'http://www.lazada.vn/apple-iphone-7-32gb-vang-hong-hang-nhap-khau-2763037.html'
iphone_7_review = scrap_product_reviews(product_url)

# Product: Samsung J3
product_url = 'http://www.lazada.vn/samsung-galaxy-j3-2016-8gb-vang-hang-phan-phoi-chinh-thuc-2513732.html'
galaxy_j3_review = scrap_product_reviews(product_url)

# Category: Dien Thoai Di Dong
category_url = 'http://www.lazada.vn/dien-thoai-di-dong/'
products_links = scrap_product_links(category_url)

products_links.to_json('products_links.json', orient='records') # Save to JSON
products_links['product_name'] = products_links['product_name'].str.replace(r'[\n\r\t]', ' ')
products_links.to_csv('products_links.tsv', sep='\t', encoding='utf-8', index=False)

# Get all products reviews in categorical Dien Thoai Di Dong
all_products_reviews = pd.DataFrame()
for idx, row in products_links.iterrows():
    product_url = row['product_url']
    product_reviews = scrap_product_reviews(product_url)
    all_products_reviews = all_products_reviews.append(product_reviews)
    
    file_json_out = '.\\reviews_json\\' + str(idx) + '.json'
    product_reviews.to_json(file_json_out, orient='records')

all_products_reviews.to_json('products_reviews.json', orient='records') # Save to JSON
#all_products_reviews.to_csv('products_reviews.tsv', sep='\t', encoding='utf-8', index=False)

#------------------------------------------------------------------------------