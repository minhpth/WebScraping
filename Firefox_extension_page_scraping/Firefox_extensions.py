#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Sat Apr 29 10:34:48 2017

@author: minh
"""

#------------------------------------------------------------------------------
# WEB SCRAPING - UPWORK PROJECT - FIREFOX EXTENSIONS PAGE
#------------------------------------------------------------------------------

"""
This project will go to Firefox extension website, make a extensions search with
a search term (e.g. Youtube, Facebook, etc.), then extract some extensions'
information (details are in below).

Firefox extension URL: https://addons.mozilla.org/en-US/firefox/extensions/

Things to do:
    1. note if firefox or chrome [Done]
    2. list of all extensions titles [Done]
    3. link to extension page [Done]
    4. search rank position for given search term [Done]
    5. numbers of active users [Done]
    6. size [Done]
    7. version [Done]
    8. date of last update [Done]
    9. # of reviews and overall rating [Done]
    10. developer/program website link [Done]
    11. developer/contact email [__???__]

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

# Other packages
import os
import sys
import re
from time import sleep
from datetime import datetime

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

def BeautifulSoup_wrapper(url, num_retry=5, delay=10):
    """
    This function will try several times to extract the HTML structure of the page
    """
    
    count_retry = 0
    while count_retry < num_retry:
        try:
            page = urlopen_wrapper(url) # Try to open the page
            soup = BeautifulSoup(page, "html.parser") # Parse the page
            return soup # If no error, end function
            
        except:
            print('ERROR extracting HTML structure. Retrying...')
            count_retry += 1
            sleep(delay)

    # If try many time but failed
    print('FAILED to extract HTML structure.', url)
    update_errorLog('FAILED_EXTRACTING_HTML' + ' | ' + url) # Add to log
    return None

def extract_addonsList(soup):
    """
    This function will extract all the name and link of Firefox extensions
    Input: an BeautifulSoup object of the first extension page
    Output: data frame contain addons' names and links
    
    Note: the number of extension pages can be different on different OS system
    """
    
    # Extract all extensions' names and links
    pageCount = 0
    addonNameList = []
    addonLinkList = []
        
    while True:
        
        # Extract all extensions' names and links of a page
        itemAddonList = soup.findAll('div', attrs={'class':'item addon'}) # This search will include "item addon incompatible"
        
        for item in itemAddonList:
            addonNameList.append(item.div.h3.a.text.strip())
            addonLinkList.append(Firefox_addonPage + item.div.h3.a.get('href')) # Can remove term '/?src=search' if needed
        
        # Print out to track
        pageCount += 1
        print('Page', pageCount, '|', len(itemAddonList), 'items extracted')
        
        # Look for Next button
        nextButton = soup.find('a', attrs={'class':'button next'})
        
        if nextButton is not None: # Go to next page
            nextUrl = Firefox_addonPage + nextButton.get('href')
            soup = BeautifulSoup_wrapper(nextUrl)
        else: # Stop the while loop
            break
        
    # Construct the data frame results
    addonTb = pd.DataFrame({'addon_name':pd.Series(addonNameList),
                            'addon_url':pd.Series(addonLinkList)},
                            columns=['addon_name', 'addon_url'])
    
    # Remove duplicated information, in some website, next page can show some
    # items from previous pages
    addonTb = addonTb.drop_duplicates().reset_index(drop=True)
    
    # Add search_rank
    addonTb['search_rank'] = addonTb.index + 1
    
    return addonTb

def extract_activeUser(addonSoup):
    """
    This function will return the number of active users in an addon page.
    If it cannot find that number, it will return None.
    """
    
    try:
        activeUser = int(re.sub('[^0-9]', '', addonSoup.find('div', attrs={'id':'daily-users'}).text.strip()))
        return activeUser
    except:
        return None
    
def extract_size(addonSoup):
    """
    This function will return the size of the addon in addon page. The size number
    will be a text with size + size unit (e.g. KiB, MB, etc.)
    If it cannot find that number, it will return None.
    """
    
    try:
        size = addonSoup.find('span', attrs={'class':'filesize'}).text.strip()
        return size
    except:
        return None
    
def extract_version(addonSoup):
    """
    This function will return the version of the addon in addon page. The result
    will be a text of version number.
    If it cannot find that text, it will return None.
    """
    
    try:
        version = re.sub('Version', '', addonSoup.find('div', attrs={'class':'version item'}).div.h3.a.text).strip()
        return version
    except:
        return None
        
def extract_releaseDate(addonSoup):
    """
    This function will return the release date of the addon in addon page. The 
    result will be a text of that date.
    If it cannot find that date, it will return None.
    """
    
    try:
        versionItem = addonSoup.find('div', attrs={'class':'version item'})
        releaseDate = versionItem.find('span', attrs={'class':'meta'}).time.get('datetime')
        return releaseDate
    except:
        return None

def extract_numberReview(addonSoup):
    """
    This function will return the number of users giving rates to this addon.
    If it cannot find that number, it will return None.
    """
    
    try:
        numberReview = int(re.sub('[^0-9]', '', addonSoup.find('span',  attrs={'itemprop':'ratingCount'}).text.strip()))
        return numberReview
    except:
        return None

def extract_avgRating(addonSoup):
    """
    This function will return the average rating of this addon.
    If it cannot find that number, it will return None.
    """
    
    try:
        avgRating = float(addonSoup.find('meta', attrs={'itemprop':'ratingValue'}).get('content'))
        return avgRating
    except:
        return None

def extract_authorName(addonSoup):
    """
    This function will return the author name from the author extension page.
    If it cannot find that name, it will return None.
    """
    
    try:
        # Get the extension URL of the author of the current extension page
        authorURL = Firefox_addonPage + addonSoup.find(attrs={'class':'author'}).a.get('href')
        authorSoup = BeautifulSoup_wrapper(authorURL)
        
        # Find author's information
        authorTb = authorSoup.find('table', attrs={'class':'person-info'}) # Get the table of information
        authorName = authorTb.find(text='Name').next.next.text.strip()
        return authorName
    except:
        return None

def extract_authorHomepage(addonSoup):
    """
    This function will return the home page of author from the author extension page.
    If it cannot find that page url, it will return None.
    """
    
    try:
        # Get the extension URL of the author of the current extension page
        authorURL = Firefox_addonPage + addonSoup.find(attrs={'class':'author'}).a.get('href')
        authorSoup = BeautifulSoup_wrapper(authorURL)
        
        # Find author's information
        authorTb = authorSoup.find('table', attrs={'class':'person-info'}) # Get the table of information
        authorHomepage = authorTb.find(text='Homepage').next.next.text.strip()
        return authorHomepage
    except:
        return None

def extract_addonInfo(addonName, addonURL, searchRank):
    """
    This function extract all information of an addon page, then return data in
    a data frame.
    """
    
    activeUser = None
    size = None
    version = None
    releaseDate = None
    numberReview = None
    avgRating = None
    authorName = None
    authorHomepage = None
    is_error = False
    
    # Initiate connection to a specific addon page
    addonSoup = BeautifulSoup_wrapper(addonURL)
    
    if addonSoup is not None: # Successful extract page HTML
        
        # Extract addon information
        activeUser = extract_activeUser(addonSoup) # Active (daily) users
        #if activeUser is None: is_error = True # Some addons may not have this field
                                       
        size = extract_size(addonSoup) # Addon size
        if size is None: is_error = True # All addons have this field
                           
        version = extract_version(addonSoup) # Addon version
        if version is None: is_error = True # All addons have this field
                                 
        releaseDate = extract_releaseDate(addonSoup) # Release date
        if releaseDate is None: is_error = True # All addons have this field
                                         
        numberReview = extract_numberReview(addonSoup) # Number of reviews
        if numberReview is None: is_error = True # All addons have this field
                                           
        avgRating = extract_avgRating(addonSoup) # Average ratings
        #if avgRating is None: is_error = True # Some addons may not have this field
                                     
        authorName = extract_authorName(addonSoup) # Auther's name
        #if authorName is None: is_error = True # Some addons may not have this field
                                       
        authorHomepage = extract_authorHomepage(addonSoup) # Author's webpage
        #if authorHomepage is None: is_error = True # Some addons may not have this field
        
    else:
        is_error = True # Mark error

    # Construct result table
    addonInfo = pd.DataFrame.from_dict({'addon_name':addonName,
                                        'addon_url':addonURL,
                                        'search_rank':searchRank,
                                        'active_user':activeUser,
                                        'size':size,
                                        'version':version,
                                        'release_date':releaseDate,
                                        'number_review':numberReview,
                                        'rating':avgRating,
                                        'author_name':authorName,
                                        'author_homepage':authorHomepage,
                                        'is_error':is_error},
                                        orient='index').T
    
    # Re-arrange columns
    addonInfo = addonInfo[['addon_name',
                           'addon_url',
                           'search_rank',
                           'active_user',
                           'size',
                           'version',
                           'release_date',
                           'number_review',
                           'rating',
                           'author_name',
                           'author_homepage',
                           'is_error']]
    
    return addonInfo

def extract_addonInfo_wrapper(addonName, addonURL, searchRank, num_retry=5, delay=10):
    """
    This function will try several times to extract the addonInfo.
    """
    
    count_retry = 0
    while  count_retry < num_retry:
        try:
            addonInfo = extract_addonInfo(addonName, addonURL, searchRank)
            return addonInfo # If no error, end function
            
        except:
            print('ERROR extracting addon info. Retrying...')
            count_retry += 1
            sleep(delay)
    
    # If try many times but failed
    print('FAILED to extract this addon information.', addonName, addonURL)
    update_errorLog('FAILED_EXTRACTING_ADDON_INFO' + ' | ' + addonName + ' | ' + addonURL) # Add to log
    return None

def extract_allAddonInfo(addonTb):
    """
    This function will go to each extension page, then extract all of their
    information if possible. The result is in data frame format.
    """
    
    addonInfoTb = pd.DataFrame()
    
    # Loop through all extension page
    addonCount = 0
    for index, row in addonTb.iterrows():
        
        addonName = row['addon_name']
        addonURL = row['addon_url']
        searchRank = row['search_rank']
        
        addonCount += 1
        print('Extension', str(addonCount) + '/' + str(addonTb.shape[0]), ':', addonName)
        
        # Extract addon info
        addonInfo = extract_addonInfo_wrapper(addonName, addonURL, searchRank)
        
        if addonInfo is None: # Failed to extract addon info
            # Construct a table to return, mark is_error = True
            addonInfo = pd.DataFrame.from_dict({'addon_name':addonName,
                                                'addon_url':addonURL,
                                                'search_rank':searchRank,
                                                'is_error':True},
                                                orient='index').T                                               
        
        # Add new row to the result table
        addonInfoTb = addonInfoTb.append(addonInfo, ignore_index=True)
        
    # Copy some columns from addonTb
    addonInfoTb['platform'] = addonTb['platform']
    addonInfoTb['search_term'] = addonTb['search_term']
        
    return addonInfoTb

def verify(addonTb, addonInfoTb):
    """
    This function will verify the data collected from addonInfoTb table with
    the given list in addonTb table
    """
    
    addonTb = addonTb.reset_index(drop=True)
    addonInfoTb = addonInfoTb.reset_index(drop=True)
    colsList = ['addon_name', 'addon_url', 'search_rank', 'search_term', 'platform']
    
    try:
        if (addonTb[colsList] == addonInfoTb[colsList]).all().all():
            return True
        else:
            return False
    except:
        return False

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Change path to working directory
    #os.chdir('/home/minh/Python/WebScraping/Firefox_extension_page_scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    # Search term identify. In the future, this can be upgraded to automatic create a url text
    searchTerm = sys.argv[1] # 'youtube'
    print('Extension search term:', searchTerm)
    
    #--------------------------------------------------------------------------    
    # STEP 1. INITIATE CONNECTION
    #--------------------------------------------------------------------------
    
    print("Step 1. Connect to the extension page")
    
    # URL global variables (DO NOT change the vars' names)
    Firefox_addonPage = "https://addons.mozilla.org"
    Firefox_searchURL = "https://addons.mozilla.org/en-US/firefox/search/?q="
    
    # Try to open the page and extract the HTML structure
    url = Firefox_searchURL + searchTerm
    soup = BeautifulSoup_wrapper(url)
    
    #--------------------------------------------------------------------------
    # STEP 2. EXTRACT ADDONS' NAMES AND LINKS
    #--------------------------------------------------------------------------
    
    print("Step 2. Extract all addons' names and links")
    
    addonTb = extract_addonsList(soup)
    addonTb['search_term'] = searchTerm
    addonTb['platform'] = 'Firefox'
    
    fileOut = 'output/' + searchTerm + '_Firefox_addonList.csv'
    addonTb.to_csv(fileOut, index=False, encoding='utf-8')
    
    #--------------------------------------------------------------------------
    # STEP 3. GO TO EACH ADDON PAGE, EXTRACT INFORMATION
    #--------------------------------------------------------------------------
    
    print('Step 3. Go to each extension page, extract their information')
    
    addonInfoTb = extract_allAddonInfo(addonTb)
    print('Verified:', verify(addonTb, addonInfoTb))
    
    fileOut = 'output/' + searchTerm + '_Firefox_addonInfo.csv'
    addonInfoTb.to_csv(fileOut, index=False, encoding='utf-8')
    
    print()
                                        
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
"""

#------------------------------------------------------------------------------