#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Thu Mar 02 16:28:08 2017

@author: MINH PHAN
"""

#------------------------------------------------------------------------------
# INDEED.FR DATA SCIENTIST SKILLS - WEB SCRAPING
#------------------------------------------------------------------------------

"""
This small project aims to explore the background (e.g. education, skills, etc.)
required for a Data Scientist / Data Analyst position in France.

Using web scraping and text mining techniques, we will collect and analyse job
postings on Indeed.fr website.

To run this script:
    python Indeed_skills_scraping.py "job name" "French location"

Important notes:
    1. This project is limit in France only (i.e. Indeed.fr). Therefore, some
    parts of the URLs' keywords, HTML elements' search terms (class name, id, 
    text, etc.) maybe apply only for French website.
    
    2. The cities name must be exactly correct by French cities or regions,
    ortherwise, the script will break.
    
    3. Due to the loading page issue, the number of jobs expect to be extracted
    at the beginning page (first page) maybe different from the ending page
    (last page). For example:
        - At the first page, Indeed.fr expects 63 job pages, 10 jobs/page
        - But in the first run, the last page we can reach is page 57
        - In the second run, the last page we can reach is page 61
        - Etc...
    
    4. Inddeef.fr shows 10 organic jobs per page, and around 5 sponsored jobs
    additionally. Some time, sponsored jobs won't load.

Environment:
    1. Ubuntu 16.04 LTS (64-bit)
    2. Python 2.7 (conda 4.3.14, selenium 2.53.6, beautifulsoup4 4.5.3)
    3. Firefox 45.0
    4. geckodriver 0.16.1 (linux64)
"""

#------------------------------------------------------------------------------
# Initiating
#------------------------------------------------------------------------------

# Data handling packages
import pandas as pd

# Web scraping packages
from bs4 import BeautifulSoup # Web scraping
from bs4 import NavigableString
from urllib import quote_plus
import urllib2
from urllib2 import urlopen # Download link

# Text mining packages
import re
from collections import Counter
from nltk.corpus import stopwords

# Other packages
import os
import sys
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

def extract_jobs(soup):
    """
    This function will extract all the jobs listing in the current page, including
    sponsored and organic jobs listing. Return a data frame.
    """
    
    # Get the whole column result of the current page
    resultsColSoup = soup.find('td', attrs={'id':'resultsCol'})
    
    # Extract all jobs
    jobsList = resultsColSoup.findAll('div', attrs={'data-jk':not None})
    
    # Loop through the jobs list to extract their infos
    jobNameList = []
    jobIdList = []
    jobURLList = []
    #originalURLList = []
    listingTypeList = []
    companyList = []
    locationList = []
    
    for jobSoup in jobsList:
        
        # Some fields can directly extract
        jobNameList.append(jobSoup.a.text.strip())
        jobIdList.append(jobSoup.get('data-jk'))
        jobURLList.append(IndeedFR_viewJobURL + jobIdList[-1])
        #originalURLList.append(urlopen_wrapper(IndeedFR_URL + jobSoup.a.get('href')).url)
        locationList.append(jobSoup.find('span', attrs={'class':'location'}).text.strip())
        
        # Some fields are different between organic and sponsored jobs listing
        listingType = jobSoup.get('data-tn-component')
        if listingType is None: # Sponsored job listing
            listingTypeList.append('sponsoredJob')
        else: # Organic job listing
            listingTypeList.append(listingType)
            
        # Some fields can be missing
        try:
            company = jobSoup.find('span', attrs={'class':'company'}).text.strip()
        except:
            company = None
        companyList.append(company)
            
    # Construct result data frame
    jobsTb = pd.DataFrame({'job_name':pd.Series(jobNameList),
                           'job_id':pd.Series(jobIdList),
                           'job_url':pd.Series(jobURLList),
                           #'original_job_url':pd.Series(originalURLList),
                           'listing_type':pd.Series(listingTypeList),
                           'company':pd.Series(companyList),
                           'location':pd.Series(locationList)},
                          columns=['job_name',
                                   'job_id',
                                   'job_url',
                                   #'original_job_url',
                                   'listing_type',
                                   'company',
                                   'location'])
    
    return jobsTb

def get_nextPageURL(soup):
    """
    This function will search for the next button. If that button exists, return
    the link for that next page.
    """
    
    nextButtonSoup = None
    pageBoxSoup = soup.find('div', attrs={'class':'pagination'})
    
    if pageBoxSoup is not None: # The page has page controlling block
        np = pageBoxSoup.find('span', attrs={'class':'np'}, text=u'Suivant\xa0\xbb')
        if np is not None: nextButtonSoup = np.parent.parent
        
    if nextButtonSoup is not None: # Next page exists
        return IndeedFR_URL + nextButtonSoup.get('href')
    else:
        return None
    
def get_total_organicJobs(soup):
    """
    This function will look for the total organic jobs listing, the result will
    be used to double check scraping process.
    """
    
    try:
        total_organicJobs = int(soup.find('div', attrs={'id':'searchCount'}).text.strip().split(' ')[-1])
        return total_organicJobs
    except:
        return 0
    
def extract_allJobs(firstPageURL):
    """
    This function will go to page by page, then extract all the jobs listing in
    that page unitl the end.
    """
    
    soup = BeautifulSoup_wrapper(firstPageURL, 'lxml')
    total_organicJobs = get_total_organicJobs(soup)
    
    allJobsTb = pd.DataFrame()
    pageCount = 0
    
    while True:
    
        # Extract all jobs in the current page
        jobsTb = extract_jobs(soup)
        
        # Print out to track
        pageCount += 1
        print('Page', pageCount, '|', len(jobsTb), 'jobs extracted')
        
        # Update the results
        allJobsTb = allJobsTb.append(jobsTb, ignore_index=True)
        
        # Find the next button url and follow it
        nextPage_url = get_nextPageURL(soup)
        if nextPage_url is not None:
            soup = BeautifulSoup_wrapper(nextPage_url)
        else:
            break
    
    # Remove duplicated information, in some website, next page can show some
    # items from previous pages
    allJobsTb = allJobsTb.drop_duplicates().reset_index(drop=True)
    
    # Add search rank
    allJobsTb['search_rank'] = allJobsTb.index + 1
    
    # Verify scrapping process
    print('Total organic jobs expected:', total_organicJobs)
    print('Total organic jobs got:', len(allJobsTb.loc[allJobsTb['listing_type']=='organicJob']))
    print('Total jobs got:', len(allJobsTb))
    
    return allJobsTb

def extract_allJobsInfo(allJobsTb):
    """
    This function loop through all jobs in the input list, then extract their
    detailed information, e.g. job description, job note, job post date-time...
    """

    # Loop through each job posting
    allJobsInfoTb = pd.DataFrame()
    jobCount = 0
    
    for index, row in allJobsTb.iterrows():
        
        # Get the job page
        #testURL = "https://www.indeed.fr/voir-emploi?jk=0a82fdb1b970f45b"
        #jobPageSoup = BeautifulSoup_wrapper(testURL, 'lxml')
        jobPageSoup = BeautifulSoup_wrapper(row['job_url'], 'lxml')
        
        jobCount += 1
        #if jobCount == 1: break
        print('Job', str(jobCount) + '/' + str(len(allJobsTb)), ':', unicode(row['job_name']), '[' + unicode(row['company']) + ']')
        
        # Extract main job post
        jobSummarySoup = jobPageSoup.find('span', attrs={'id':'job_summary', 'class':'summary'})
        jobPost = jobSummarySoup.text
        
        # Extract job posting date
        infoBoxSoup = jobSummarySoup.next_sibling.next_sibling.div
        postDate = re.sub('il y a', '', infoBoxSoup.find('span', attrs={'class':'date'}).text).strip()
        
        # Extract job notes
        jobHeaderSoup = jobPageSoup.find('div', attrs={'data-tn-component':'jobHeader'})
        jobNoteSoup = jobHeaderSoup.find(attrs={'class':'location'}).next_sibling # Ignore class company and location
                                        
        jobNote = ''
        while jobNoteSoup is not None: # Loop through all element, ignore NavigableString
            if not isinstance(jobNoteSoup, NavigableString): jobNote = jobNote + jobNoteSoup.text # Extract text
            jobNoteSoup = jobNoteSoup.next_sibling # Next element
        jobNote = jobNote.strip()
        
        # Construct result table
        row['job_description'] = jobPost
        row['job_note'] = jobNote
        row['post_from'] = postDate
        row['sraping_date'] = str(datetime.now())
        allJobsInfoTb = allJobsInfoTb.append(row, ignore_index=True)
        
    return allJobsInfoTb

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Change path to working directory
    #os.chdir('/home/minh/Python/WebScraping/Indeed_skills_scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    # Search term identify
    jobSearch_name = sys.argv[1] # 'data analyst'
    jobSearch_location = sys.argv[2] # 'Paris'
    print('Job search:', jobSearch_name, '|', 'Location:', jobSearch_location)
    
    #--------------------------------------------------------------------------    
    # STEP 1. INITIATE CONNECTION
    #--------------------------------------------------------------------------
    
    print("Step 1. Connect to the main page")
    
    # URL global variables (DO NOT change the vars' names)
    IndeedFR_URL = "https://www.indeed.fr"
    IndeedFR_jobSearchURL = "https://www.indeed.fr/emplois?q="
    IndeedFR_viewJobURL = "https://www.indeed.fr/voir-emploi?jk="
    
    # Try to open the page and extract the HTML structure
    firstPageURL = IndeedFR_jobSearchURL + quote_plus(jobSearch_name) + '&l=' + quote_plus(jobSearch_location)
    soup = BeautifulSoup_wrapper(firstPageURL)
    
    #--------------------------------------------------------------------------
    # STEP 2. EXTRACT ALL JOBS' BASIC INFORMATION
    #--------------------------------------------------------------------------
    
    print("Step 2. Extract and create a jobs list")

    allJobsTb = extract_allJobs(firstPageURL)
    fileOut = 'output/' + slugify(jobSearch_name) + '_' + slugify(jobSearch_location) + '_jobList.csv'
    allJobsTb.to_csv(fileOut, index=False, encoding='utf-8')
    
    #--------------------------------------------------------------------------
    # STEP 3. LOOP THROUGH EACH JOB, EXTRACT ALL JOBS' FULL INFORMATION
    #--------------------------------------------------------------------------
    
    print("Step 3. Loop through all jobs and extract detailed information")
    
    allJobsInfoTb = extract_allJobsInfo(allJobsTb)
    fileOut = 'output/' + slugify(jobSearch_name) + '_' + slugify(jobSearch_location) + '_jobsInfo.pkl'
    allJobsInfoTb.to_pickle(fileOut) # DO NOT save to CSV (or TSV), text field will create a big mess
    
    print()
    
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
Further researches:
    1. Why the numbers of jobs extracted are not the same as showing at the 
    first page? Any loading problems here?
    
    2. Why the HTML structure extracted by BeautifulSoup is different from the
    HTML structure showing in Chrome website source code?
    For example: https://www.indeed.fr/voir-emploi?jk=0a82fdb1b970f45b
    -> SOLUTION: Use LXML parser rather than HTML parser
    
Refs:
    1. Different parsers: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
    2. Indeed web scraping project: https://jessesw.com/Data-Science-Skills/
    3. Using SQL database with Pandas: https://www.dataquest.io/blog/python-pandas-databases/
"""

#------------------------------------------------------------------------------