#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Sat Apr 29 10:34:48 2017

@author: minh
"""

#------------------------------------------------------------------------------
# WEB SCRAPPING - UPWORK PROJECT - FIREFOX EXTENSIONS PAGE
#------------------------------------------------------------------------------

"""
This project will go to Firefox extension website, make a extensions search with
a search term (e.g. Youtube, Facebook, etc.), then extract some extensions'
information (details are in below).

Firefox extension URL: https://addons.mozilla.org/en-US/firefox/extensions/

Things to do:

1. note if firefox or chrome [__???__]
2. list of all extensions titles [Done]
3. link to extension page [Done]
4. search rank position for given search term [__???__]
5. numbers of active users [Done]
6. size [Done]
7. version [Done]
8. date of last update [Done]
9. # of reviews and overall rating [Done]
10. developer/program website link [Done]
11. developer/contact email [__???__]
"""

#------------------------------------------------------------------------------
# Libraries
#------------------------------------------------------------------------------

# Data handling packages
import pandas as pd

# Web scrapping packages
from bs4 import BeautifulSoup # Web scrapping
import urllib2
from urllib2 import urlopen # Download link

# Other packages
import os
import re
from time import sleep

#------------------------------------------------------------------------------
# Self-defined functions
#------------------------------------------------------------------------------

def urlopen_wrapper(url, num_retry=3, delay=10):
    """
    Function to open a page, try several times if the page gets stuck
    """
    
    count_retry = 0
    while  count_retry < num_retry:
        try:
            page = urlopen(url, timeout=30)
            return page # If no error, end function
            
        except urllib2.URLError as e:
            print('Page load error:', e)
            print('Waiting and retrying...')
            count_retry += 1
            sleep(delay)
    
    # If try many times but failed
    print('Failed to load page...')
    return None

def BeautifulSoup_wrapper(url, num_retry=3, delay=5):
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
            print('Extract HTML structure error. Retrying...')
            count_retry += 1
            sleep(delay)

    # If try many time but failed
    print('Failed to extract HTML structure...')
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
            #print(item.div.h3.a.text)
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
    
    return addonTb

def extract_activeUser(addonSoup):
    """
    This function will return the number of active users in an addon page.
    If it cannot find that number, it will return 0.
    """
    
    try:
        activeUser = int(re.sub('[^0-9]', '', addonSoup.find('div', attrs={'id':'daily-users'}).text.strip()))
        return activeUser
    except:
        return 0
    
def extract_size(addonSoup):
    """
    This function will return the size of the addon in addon page. The size number
    will be a text with size + size unit (e.g. KiB, MB, etc.)
    If it cannot find that number, it will return blank string.
    """
    
    try:
        size = addonSoup.find('span', attrs={'class':'filesize'}).text.strip()
        return size
    except:
        return ''
    
def extract_version(addonSoup):
    """
    This function will return the version of the addon in addon page. The result
    will be a text begin with "Version" + version number.
    If it cannot find that number, it will return and blank string.
    """
    
    try:
        version = addonSoup.find('div', attrs={'class':'version item'}).div.h3.a.text.strip()
        return version
    except:
        return ''
        
def extract_releaseDate(addonSoup):
    """
    This function will return the release date of the addon in addon page. The 
    result will be a text of that date.
    If it cannot find that number, it will return and blank string.
    """
    
    try:
        versionItem = addonSoup.find('div', attrs={'class':'version item'})
        releaseDate = versionItem.find('span', attrs={'class':'meta'}).time.get('datetime')
        return releaseDate
    except:
        return ''

def extract_numberReview(addonSoup):
    """
    This function will return the number of users giving rates to this addon.
    If it cannot find that number, it will return 0.
    """
    
    try:
        numberReview = int(addonSoup.find('span',  attrs={'itemprop':'ratingCount'}).text.strip())
        return numberReview
    except:
        return 0

def extract_avgRating(addonSoup):
    """
    This function will return the average rating of this addon.
    If it cannot find that number, it will return value 0.0 (float).
    """
    
    try:
        avgRating = float(addonSoup.find('meta', attrs={'itemprop':'ratingValue'}).get('content'))
        return avgRating
    except:
        return 0.0

def extract_authorInfo(addonSoup):
    """
    This function will extract all information of the author if possible.
    """
    
    def extract_authorName(authorSoup):
        """
        This function will return the author name from the author extension page.
        If it cannot find that name, it will return a blank string.
        """
        
        try:
            authorTb = authorSoup.find('table', attrs={'class':'person-info'}) # Get the table of information
            authorName = authorTb.find(text='Name').next.next.text.strip()
            return authorName
        except:
            return ''
        
    def extract_authorHomepage(authorSoup):
        """
        This function will return the home page of author from the author extension page.
        If it cannot find that page url, it will return a blank string.
        """
        
        try:
            authorTb = authorSoup.find('table', attrs={'class':'person-info'}) # Get the table of information
            authorHomepage = authorTb.find(text='Homepage').next.next.text.strip()
            return authorHomepage
        except:
            return ''
    
    # Get the extension URL of the author of the current extension page
    authorURL = Firefox_addonPage + addonSoup.find(attrs={'class':'author'}).a.get('href')
    authorSoup = BeautifulSoup_wrapper(authorURL)

    authorName = extract_authorName(authorSoup)
    authorHomepage = extract_authorHomepage(authorSoup)
    
    return authorName, authorHomepage

def extract_addonInfo(addonName, addonURL):
    """
    This function extract all information of an addon page, then return data in
    a data frame.
    """
    
    # Initiate connection to a specific addon page
    addonSoup = BeautifulSoup_wrapper(addonURL)
    
    # Extract addon information
    activeUser = extract_activeUser(addonSoup) # Active (daily) users
    size = extract_size(addonSoup) # Addon size
    version = extract_version(addonSoup) # Addon version
    releaseDate = extract_releaseDate(addonSoup) # Release date
    numberReview = extract_numberReview(addonSoup) # Number of reviews
    avgRating = extract_avgRating(addonSoup) # Average ratings
    authorName, authorHomepage = extract_authorInfo(addonSoup) # Extrac author info
    
    # Construct result table
    addonInfo = pd.DataFrame.from_dict({'addon_name':addonName,
                                        'addon_url':addonURL,
                                        'active_user':activeUser,
                                        'size':size,
                                        'version':version,
                                        'release_date':releaseDate,
                                        'number_review':numberReview,
                                        'rating':avgRating,
                                        'author_name':authorName,
                                        'author_homepage':authorHomepage},
                                        orient='index').T
    
    # Re-arrange columns
    addonInfo = addonInfo[['addon_name', 'addon_url', 'active_user',
                           'size', 'version', 'release_date', 'number_review',
                           'rating', 'author_name', 'author_homepage']]
    
    return addonInfo

def extract_allAddonInfo(addonTb):
    """
    This function will go to each extension page, then extract all of their
    information if possible. The result is in data frame format.
    """
    
    addonInfoTb = pd.DataFrame()
    
    # Loop through all extension page
    addonCount = 0
    for index, row in addonTb.iterrows():
        addonName, addonURL = row[0], row[1]
        addonCount += 1
        print('Extension', str(addonCount) + '/' + str(addonTb.shape[0]), ':', addonName)
        
        addonInfo = extract_addonInfo(addonName, addonURL)
        addonInfoTb = addonInfoTb.append(addonInfo, ignore_index=True)
        
    return addonInfoTb

def verify(addonTb, addonInfoTb):
    """
    This function will verify the data collected from addonInfoTb table with
    the given list in addonTb table
    """
    
    addonTb = addonTb.reset_index(drop=True)
    addonInfoTb = addonInfoTb.reset_index(drop=True)
    
    if (addonTb == addonInfoTb[['addon_name', 'addon_url']]).all().all():
        return True
    else:
        return False

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Change path to working directory
    os.chdir(os.path.join('/', 'home', 'minh', 'Python', 'WebScrapping', 'Firefox_extensions'))

    #--------------------------------------------------------------------------    
    # STEP 1. INITIATE CONNECTION
    #--------------------------------------------------------------------------
    
    print("Step 1. Connect to the extension page")
    
    # Search term identify
    # In the future, this can be upgraded to auto-matic create a url text
    searchTerm = 'youtube'
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
    fileOut = 'output/' + searchTerm + '_addonList.csv'
    addonTb.to_csv(fileOut, index=False, encoding='utf-8')
    
    #--------------------------------------------------------------------------
    # STEP 3. GO TO EACH ADDON PAGE, EXTRACT INFORMATION
    #--------------------------------------------------------------------------
    
    print('Step 3. Go to each extension page, extract their information')
    
    addonInfoTb = extract_allAddonInfo(addonTb)
    print('Verified:', verify(addonTb, addonInfoTb))
    
    fileOut = 'output/' + searchTerm + '_addonInfo.csv'
    addonInfoTb.to_csv(fileOut, index=False, encoding='utf-8')
                                        
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
"""

#------------------------------------------------------------------------------