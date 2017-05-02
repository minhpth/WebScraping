#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Thu Mar 02 16:28:08 2017

@author: MINH PHAN
"""

#------------------------------------------------------------------------------
# INDEED WEB SCRAPING - DATA SCIENTIST SKILLS
#------------------------------------------------------------------------------

"""
This small project aims to explore the background (e.g. education, skills, etc.)
required for a Data Scientist position. Using web scraping and text mining
techniques, we will collect and analyse job postings on Indeed.com website.
"""

#------------------------------------------------------------------------------
# Initiating
#------------------------------------------------------------------------------

# Set working path
import os
os.chdir('C:\\Users\\MINH PHAN\\Desktop\\Data_Scientist_Skills\\Indeed')

# Packages for doing web scraping
from bs4 import BeautifulSoup
import urllib2
import requests
from time import sleep

# Packages for text mining
import re
from collections import Counter
from nltk.corpus import stopwords

# Packages for process and store data
import pandas as pd

#------------------------------------------------------------------------------
# Self-defined functions
#------------------------------------------------------------------------------

def url_request(url, trying_times=3, sleeping_time=10):
    """
    This function will request an URL, if it failed then try again several times.
    Inputs: URL
    Outputs: site object (if successful) or None object (if failed)
    """
    
    trying_count = 0 # Count numbers of trying requesting url
    flag_success = False # Control flag
    
    try: # This try wrapper is used to handle invalid URL
    
        # Try to request the URL in several times
        while trying_count < trying_times:
            
            trying_count += 1
            site = requests.get(url) # Request the URL
            
            if site.ok: # If successful, stop the loop
                flag_success = True
                break
            else: # If unsucessful, wait for a while
                sleep(sleeping_time)
                
    except:
        print('Invalid URL:', url)
        pass # Do nothing

    # If successfully get the site, return it, else return None value            
    if flag_success and site.ok:
        return site
    else:
        return None
        
def get_page_text(url):
    """
    This function will try to open the page URL, get the text and clean it.
    Inputs:
    Outputs:
    """
    
    # Step 1: Get the site HTML structure
    site = url_request(url)
    
    if site is None: # Check if the site is successful request
        print('Cannot request this site:', url)
        return None
    
    soup_obj = BeautifulSoup(site.content) # Get HTML structure of the site
    
    # Step 2: Extract and clean text
    for script in soup_obj(["script", "style"]):
        script.extract() # Remove useless elements for the HTML body
    
    text = soup_obj.get_text().encode('utf-8') # Extract text from HTML
    
    # Clean text
    text = re.sub(r'[\n\r\t]', ' ', text) # Remove line breaks, tabs, etc.
    text = re.sub(r' +', ' ', text).strip() # Replace multiple spaces with one space
    text = text.decode('unicode_escape').encode('ascii', 'ignore') # Clean Unicode junks. COOL!!!
    
    # Step 3: Clean words
    text = re.sub('[^a-zA-Z.+3]', ' ', text) # Keep only alphabet characters, remove the rest
    text = text.lower().split() # Lowercase and slipt to words list
    
    # Remove all stopwords
    stop_words = set(stopwords.words("english"))
    text = [w for w in text if not w in stop_words]
    
    text = list(set(text)) # Keep only unique words
    
    return text

def indeed_scrapping(job_title, place=''):
    """
    This functions will actually do the web-scraping on Indeed.fr
    """
    
    # Step 1: Build the first URL
    base_url = 'https://www.indeed.fr'
    job_page_url = base_url + '/emplois?q='
    job_title = '+'.join(job_title.split())
    
    page_url = (job_page_url +              # Original URL
                '%22' + job_title + '%22'   # Job title
                '&l=' + place               # Location
    )
    
    # Step 2: Loop through all page and scrap the information
    
    # Get HTML structure of the site
    site = url_request(page_url) # Request the site
    
    if site is None: # Check if the site is successful request
        print('Cannot request this site:', page_url)
        return None
    
    soup_obj = BeautifulSoup(site.content) # Get HTML structure of the site
    
    # Get all the job links from the current page
    job_links_obj = soup_obj.find_all(name='a', attrs={'data-tn-element':'jobTitle'})
    job_links_list = [base_url + job_link.get('href') for job_link in job_links_obj]
    
    # Find the next button and get the action link
    next_button = soup_obj.find(name='span', attrs={'class':'np'})
    
    if next_button is 

#------------------------------------------------------------------------------
#
#------------------------------------------------------------------------------


def skills_info(city = None, state = None):
    """
    This function will take a desired city/state and look for all new job postings
    on Indeed.com. It will crawl all of the job postings and keep track of how many
    use a preset list of typical data science skills. The final percentage for each skill
    is then displayed at the end of the collation. 
        
    Inputs: The location's city and state. These are optional. If no city/state is input, 
    the function will assume a national search (this can take a while!!!).
    Input the city/state as strings, such as skills_info('Chicago', 'IL').
    Use a two letter abbreviation for the state.
    
    Output: A bar chart showing the most commonly desired skills in the job market for 
    a data scientist. 
    """
        
    final_job = 'data+scientist' # searching for data scientist exact fit("data scientist" on Indeed search)
    
    # Make sure the city specified works properly if it has more than one word (such as San Francisco)
    if city is not None:
        final_city = city.split() 
        final_city = '+'.join(word for word in final_city)
        final_site_list = ['http://www.indeed.com/jobs?q=%22', final_job, '%22&l=', final_city,
                    '%2C+', state] # Join all of our strings together so that indeed will search correctly
    else:
        final_site_list = ['http://www.indeed.com/jobs?q="', final_job, '"']

    final_site = ''.join(final_site_list) # Merge the html address together into one string
    
    base_url = 'http://www.indeed.com'
    
    try:
        html = urllib2.urlopen(final_site).read() # Open up the front page of our search first
    except:
        'That city/state combination did not have any jobs. Exiting . . .' # In case the city is invalid
        return None
    
    soup = BeautifulSoup(html) # Get the html from the first page
    
    # Now find out how many jobs there were
    
    num_jobs_area = soup.find(id = 'searchCount').string.encode('utf-8') # Now extract the total number of jobs found
                                                                        # The 'searchCount' object has this
    
    job_numbers = re.findall('\d+', num_jobs_area) # Extract the total jobs found from the search result
    
    if len(job_numbers) > 3: # Have a total number of jobs greater than 1000
        total_num_jobs = (int(job_numbers[2])*1000) + int(job_numbers[3])
    else:
        total_num_jobs = int(job_numbers[2]) 
    
    city_title = city
    if city is None:
        city_title = 'Nationwide'
        
    print('There were', total_num_jobs, 'jobs found,', city_title) # Display how many jobs were found
    
    num_pages = int(total_num_jobs/10) # This will be how we know the number of times we need to iterate over each new
                                      # search result page
    job_descriptions = [] # Store all our descriptions in this list
    
    for i in xrange(1,num_pages+1): # Loop through all of our search result pages
        print('Getting page', i)
        start_num = str(i*10) # Assign the multiplier of 10 to view the pages we want
        current_page = ''.join([final_site, '&start=', start_num])
        # Now that we can view the correct 10 job returns, start collecting the text samples from each
            
        html_page = urllib2.urlopen(current_page).read() # Get the page
            
        page_obj = BeautifulSoup(html_page) # Locate all of the job links
        job_link_area = page_obj.find(id = 'resultsCol') # The center column on the page where the job postings exist
            
        job_URLS = [base_url + link.get('href') for link in job_link_area.find_all('a')] # Get the URLS for the jobs
            
        job_URLS = filter(lambda x:'clk' in x, job_URLS) # Now get just the job related URLS
            
        for j in xrange(0,len(job_URLS)):
            final_description = text_cleaner(job_URLS[j])
            if final_description: # So that we only append when the website was accessed correctly
                job_descriptions.append(final_description)
            sleep(1) # So that we don't be jerks. If you have a very fast internet connection you could hit the server a lot! 
        
    print('Done with collecting the job postings!')
    print('There were', len(job_descriptions), 'jobs successfully found.')
    
    doc_frequency = Counter() # This will create a full counter of our terms. 
    [doc_frequency.update(item) for item in job_descriptions] # List comp
    
    # Now we can just look at our final dict list inside doc_frequency
    
    # Obtain our key terms and store them in a dict. These are the key data science skills we are looking for
    
    prog_lang_dict = Counter({'R':doc_frequency['r'], 'Python':doc_frequency['python'],
                    'Java':doc_frequency['java'], 'C++':doc_frequency['c++'],
                    'Ruby':doc_frequency['ruby'],
                    'Perl':doc_frequency['perl'], 'Matlab':doc_frequency['matlab'],
                    'JavaScript':doc_frequency['javascript'], 'Scala': doc_frequency['scala']})
                      
    analysis_tool_dict = Counter({'Excel':doc_frequency['excel'],  'Tableau':doc_frequency['tableau'],
                        'D3.js':doc_frequency['d3.js'], 'SAS':doc_frequency['sas'],
                        'SPSS':doc_frequency['spss'], 'D3':doc_frequency['d3']})  

    hadoop_dict = Counter({'Hadoop':doc_frequency['hadoop'], 'MapReduce':doc_frequency['mapreduce'],
                'Spark':doc_frequency['spark'], 'Pig':doc_frequency['pig'],
                'Hive':doc_frequency['hive'], 'Shark':doc_frequency['shark'],
                'Oozie':doc_frequency['oozie'], 'ZooKeeper':doc_frequency['zookeeper'],
                'Flume':doc_frequency['flume'], 'Mahout':doc_frequency['mahout']})
                
    database_dict = Counter({'SQL':doc_frequency['sql'], 'NoSQL':doc_frequency['nosql'],
                    'HBase':doc_frequency['hbase'], 'Cassandra':doc_frequency['cassandra'],
                    'MongoDB':doc_frequency['mongodb']})
                     
    overall_total_skills = prog_lang_dict + analysis_tool_dict + hadoop_dict + database_dict # Combine our Counter objects
    
    final_frame = pd.DataFrame(overall_total_skills.items(), columns = ['Term', 'NumPostings']) # Convert these terms to a 
                                                                                                # dataframe 
    # Change the values to reflect a percentage of the postings 
    
    final_frame.NumPostings = (final_frame.NumPostings)*100/len(job_descriptions) # Gives percentage of job postings 
                                                                                    #  having that term 
    
    # Sort the data for plotting purposes
    
    final_frame.sort(columns = 'NumPostings', ascending = False, inplace = True)
    
    # Get it ready for a bar plot
        
    final_plot = final_frame.plot(x = 'Term', kind = 'bar', legend = None, 
                            title = 'Percentage of Data Scientist Job Ads with a Key Skill, ' + city_title)
        
    final_plot.set_ylabel('Percentage Appearing in Job Ads')
    fig = final_plot.get_figure() # Have to convert the pandas plot object to a matplotlib object
        
        
    return fig, final_frame # End of the function