#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Fri May  5 17:59:25 2017

@author: minh
"""

#------------------------------------------------------------------------------
# TRIPADVISOR.COM TOURISM LOCATIONS SCRAPING - PHANTOMJS
#------------------------------------------------------------------------------

"""
This small project aims to collect all the tourism locations related to a city
or country listing on TripAdvisor.com

Note:
    1. To run this script: python TripAdvisor_scraping.py "location name"
    2. Move the mouse out of the Firefox window
    3. The location name should be in the format: CITY, COUNTRY

Environment:
    1. Ubuntu 16.04 LTS (64-bit)
    2. Python 2.7 (conda 4.3.14, selenium 2.53.6, beautifulsoup4 4.5.3)
    3. Firefox 45.0
    4. geckodriver 0.16.1 (linux64)
"""
        
#------------------------------------------------------------------------------
# Libraries
#------------------------------------------------------------------------------

# Data handling packages
import pandas as pd

# Web scraping packages
from bs4 import BeautifulSoup # Web scraping
import urllib2
from urllib2 import urlopen # Download link

# If selenium does not run, do these things:
# (1) Downgrade it: pip install selenium==2.53.6
# (2) Downgrade Firefox to version 46
from selenium import webdriver as web # Open a web browser
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.common.keys import Keys

# Other packages
import os
import sys
import re
from time import sleep
from datetime import datetime
import unicodedata

#------------------------------------------------------------------------------
# Self-defined functions
#------------------------------------------------------------------------------

def update_errorLog(text):
    """
    This function will append the error log file in ./log folder.
    """
    
    with open('log/errorsLog.txt', 'a') as f:
        f.write(str(datetime.now()) + ' : ' + text)
        f.write('\n')

def urlopen_wrapper(url, num_retry=5, delay=10):
    """
    Function to open a page, try several times if the page gets stuck
    """
    
    count_retry = 0
    while  count_retry < num_retry:
        try:
            page = urlopen(url, timeout=30)
            return page # If no error, end function
            
        except urllib2.URLError as e:
            print('ERROR opening url:', e)
            print('Retrying...')
            count_retry += 1
            sleep(delay)
    
    # If try many times but failed
    print('FAILED to open this url.', url)
    update_errorLog('FAILED_OPENING_URL' + ' | ' + url) # Add to log
    return None

def BeautifulSoup_wrapper(url, parser_type='lxml', num_retry=5, delay=10):
    """
    This function will try several times to extract the HTML structure of the page
    """
    
    count_retry = 0
    while count_retry < num_retry:
        try:
            page = urlopen_wrapper(url) # Try to open the page
            soup = BeautifulSoup(page, parser_type) # Parse the page
            return soup # If no error, end function
            
        except:
            print('ERROR extracting HTML structure. Retrying...')
            count_retry += 1
            sleep(delay)

    # If try many time but failed
    print('FAILED to extract HTML structure.', url)
    update_errorLog('FAILED_EXTRACTING_HTML' + ' | ' + url) # Add to log
    return None

def click_wrapper(object_click, num_retry=5, delay=5):    
    """
    Function to simulate a click, try several times if cannot click
    """
    
    count_retry = 0
    while  count_retry < num_retry:
        try:
            object_click.click()
            #print('Click successful!')
            return True
            
        except:
            print('ERROR clicking. Retrying...')
            count_retry += 1
            sleep(delay)
    
    # If try many time but failed
    print('FAILED to click on this object.')
    update_errorLog('FAILED_CLICKING_OBJECT' + ' | ' + object_click.text.strip()) # Add to log
    return False

def slugify(string):
    """
    This small function convert a search term (string) to another string that
    can be used to name the file.
    """
    
    return re.sub(r'[-\s]+', '-',
            str(re.sub(r'[^\w\s-]', '',
                unicodedata.normalize('NFKD', unicode(string))
                .encode('ascii', 'ignore'))
                .strip()
                .lower()))
   
def extract_tourismLocations(beginURL):
    """
    This function will loop through page by page of TripAdvisor and extract all
    tourism names and their page links until can not find the Next button to
    continue.
    """
    
    locationNameList = []
    locationLinkList = []
    pageCount = 0
    currentURL = beginURL
    
    while True: # Loop until cannot find next button

        # Extract the HTML structure of the page
        soup = BeautifulSoup_wrapper(currentURL, 'lxml')
        
        # Extract all location text
        countLocation = 0
        for dest in soup.findAll('div', attrs={"class": "listing_title"}):
            locationNameList.append(dest.text.strip())
            locationLinkList.append(TripAdvisor_url + dest.a.get('href'))
            countLocation += 1
        
        # Print out to track
        pageCount += 1
        print('Page', str(pageCount), ':', countLocation, 'locations extracted')
        
        # Find Next button
        nextButtonSoup = soup.find(attrs={"class": "nav next rndBtn ui_button primary taLnk"})
        disabled_nextButtonSoup = soup.findAll(attrs={"class": "nav next disabled"})
        
        # Check the NEXT button, if it was blocked, end loop
        if (nextButtonSoup is None) or disabled_nextButtonSoup: break
        
        # Else, jump to next page, continue loop
        currentURL = TripAdvisor_url + str(nextButtonSoup.get('href'))
    
    # Construct result table
    locationTb = pd.DataFrame({'location_name':pd.Series(locationNameList),
                               'location_url':pd.Series(locationLinkList)},
                              columns=['location_name',
                                       'location_url'])
    
    # Add the search rank
    locationTb['search_rank'] = locationTb.index + 1
    
    return locationTb

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Change path to working directory
    #os.chdir('/home/minh/Python/WebScraping/TripAdvisor_tourism_locations_scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    # Search term identify
    searchTerm = sys.argv[1]
    #searchTerm = 'Paris'
    print('Location name:', searchTerm)
    
    #--------------------------------------------------------------------------
    # STEP 1. INITIATE CONNECTION
    #--------------------------------------------------------------------------

    print("Step 1. Connect to main page")

    TripAdvisor_url = 'https://www.tripadvisor.com'
    TripAdvisor_attractions = 'https://www.tripadvisor.com/Attractions'
    TripAdvisor_searchPage = 'https://www.tripadvisor.com/Search?redirect=true'
    
    while True: # Loop until get the right version of the page
        #driver = web.Firefox()
        driver = web.PhantomJS()
        #driver.set_window_position(0, 0) # Move windows to the top-left corner
        driver.get(TripAdvisor_attractions)
        
        # Check if the page is old version or 2017 new version
        try:
            pageDescription = driver.find_element_by_css_selector('.rebrand_2017.HomeRebranded.js_logging')
        except:
            pageDescription = None
            
        if pageDescription is not None:
            print('TripAdvisor.com new version page. Reload...')
            driver.quit()
        else:
            break
    
    #--------------------------------------------------------------------------
    # STEP 2. GET THE FIRST PAGE SHOWING TOURISM LOCATIONS
    #--------------------------------------------------------------------------
    
    print('Step 2. Do the search on the page')
    
    # Input search term (city/location's name) into search box of the page
    locationBox = driver.find_element_by_id('SEARCHBOX')
    locationBox.clear()
    for k in list(searchTerm): # Stimulate keyboard typing input
        locationBox.send_keys(k)
        sleep(0.2)
    # locationBox.send_keys(Keys.TAB)
    
    # Press SEARCH
    searchButton = driver.find_element_by_id('SUBMIT_ATTRACTIONS')
    click_wrapper(searchButton)
    
    # Cannot find the location, redirect to Search page
    # URL: https://www.tripadvisor.com/Search?redirect=true&type=eat&q=UK
    wait(driver, 30).until(lambda driver: driver.current_url != TripAdvisor_attractions) # Check if the browser is move the next page or not
    curentURL = driver.current_url
    if curentURL[:len(TripAdvisor_searchPage)] == TripAdvisor_searchPage:
        print('ERROR. Cannot find city name. Program exits...')
        update_errorLog('CITY_NAME_NOT_FOUND' + ' | ' + searchTerm)
        sys.exit()
    
    # Get the first page URL to begin scraping tourism locations
    wait(driver, 30).until(lambda driver: driver.find_element_by_class_name('attraction_clarity_cell')) # Wait a bit for the page to load
    beginURL = driver.current_url
    
    # Get actualy location results, sometime, the location we want to search does
    # not exist on TripAdvisor
    actualLocationBox = driver.find_element_by_id('GEO_SCOPED_SEARCH_INPUT')
    actualLocation = actualLocationBox.get_attribute('value')
    
    driver.quit()
    
    #--------------------------------------------------------------------------
    # STEP 3. SCRAP TOURISM LOCATIONS
    #--------------------------------------------------------------------------

    print('Step 3. Scraping tourism locations')
    
    # Run webscraping
    locationTb = extract_tourismLocations(beginURL)
    
    # Create clean location keywords
    locationTb['search_term'] = searchTerm
    locationTb['location_found'] = actualLocation
    #df['location_keyword'] = df['location'].str.replace(r'(\([0-9]+\))', ' ')
    #df['location_keyword'] = df['location_keyword'].str.replace(r'[^a-zA-Z0-9]', ' ')
    #df['location_keyword'] = df['location_keyword'].str.replace(r' +', ' ')
    #df['location_keyword'] = df['location_keyword'].str.strip().str.lower()
    
    # Save to file
    fileOut = 'output/' + slugify(searchTerm) + '_locationInfo.csv'
    locationTb.to_csv(fileOut, encoding='utf-8', index=False)
    
    print()

#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
Further researches:
    1. TripAdvisors is doing A/B testing on their site. Sometimes, the site you
    recieve is not the same version with the current one. How to detect?
    -> SOLUTION: Read the page source code and find out the differences.
    
Refs:
    1. Install PhantomJS: http://stackoverflow.com/questions/36839635/how-to-update-phantomjs-1-9-8-to-phantomjs-2-1-1-on-ubuntu/36843608#36843608
    Remove it first: sudo apt purge phantomjs
"""

#------------------------------------------------------------------------------