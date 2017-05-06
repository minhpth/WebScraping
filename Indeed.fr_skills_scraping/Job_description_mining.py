#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Wed May  3 17:54:20 2017

@author: minh
"""

#------------------------------------------------------------------------------
# INDEED.FR DATA SCIENTIST SKILLS - TEXT MINING
#------------------------------------------------------------------------------

"""
This small project aims to explore the background (e.g. education, skills, etc.)
required for a Data Scientist / Data Analyst position in France.

Using web scraping and text mining techniques, we will collect and analyse job
postings on Indeed.fr website.

To run this script:
    python Job_description_mining.py [/pickle/file/path]

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

# Text mining packages
import re
from collections import Counter
import nltk
from nltk import bigrams
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
    
def myTokenizer(text):
    """
    This function will break a text (string) into a list of tokens. Then doing
    some specific text cleansing.
    """
    
    # Pattern to remove
    number_pattern = r'(^[0-9]+[.,]*[0-9]+$)|(^[0-9]+$)'
    specialChars_pattern = r'^[^\w]+$'
    stopwordsFrench = stopwords.words('french')
    stopwordsEnglish = stopwords.words('english')
    
    # Get rid of non-char
    #text = re.sub("[^a-zA-Z.+3]"," ", text) # Except alphabet, . and 3 (for d3.js), + (for C++)
    
    # Tokenize and lowercase
    tokens = [tk.lower() for tk in text.split()]
    
    # Remove number only tokens
    tokens = [tk for tk in tokens if re.match(number_pattern, tk) is None]
    
    # Remove special character only tokens
    tokens = [tk for tk in tokens if re.match(specialChars_pattern, tk) is None]
    
    # Remove English and French stopwords
    tokens = [tk for tk in tokens if tk not in stopwordsFrench]
    tokens = [tk for tk in tokens if tk not in stopwordsEnglish]
    
    return tokens + list(bigrams(tokens))

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Change path to working directory
    os.chdir('/home/minh/Python/WebScraping/Indeed.fr_skills_scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    #--------------------------------------------------------------------------    
    # STEP 1. LOAD DATA FILE
    #--------------------------------------------------------------------------
    
    print("Step 1. Load jobs description and prepare corpus")

    # Load data file
    dataPath = "/home/minh/Python/WebScraping/Indeed.fr_skills_scraping/output/data-analyst_france_jobsInfo.pkl"
    #dataPath = sys.argv[1]
    jobsPostTb = pd.read_pickle(dataPath)
    
    #--------------------------------------------------------------------------
    # STEP 2. SKILLS ANALYSIS
    #--------------------------------------------------------------------------
    
    print("Step 2. Jobs' skills analysis")

    # Prepare corpus, tokens
    corpus = jobsPostTb['job_description'].tolist()    
    lines = [line for jd in corpus for line in jd.splitlines() if line != '']
    linesTokened = [myTokenizer(line) for line in lines]
       
    # Count terms frequency
    doc_frequency = Counter()
    temp = [doc_frequency.update(line) for line in linesTokened]
    
    prog_lang_dict = Counter({'R':doc_frequency['r'],
                              'Python':doc_frequency['python'],
                              'Java':doc_frequency['java'],
                              'C++':doc_frequency['c++'],
                              'Ruby':doc_frequency['ruby'],
                              'Perl':doc_frequency['perl'],
                              'Matlab':doc_frequency['matlab'],
                              'JavaScript':doc_frequency['javascript'],
                              'Scala': doc_frequency['scala']})
                      
    analysis_tool_dict = Counter({'Excel':doc_frequency['excel'],
                                  'Tableau':doc_frequency['tableau'],
                                  'D3.js':doc_frequency['d3.js'],
                                  'SAS':doc_frequency['sas'],
                                  'SPSS':doc_frequency['spss'],
                                  'D3':doc_frequency['d3']})  

    hadoop_dict = Counter({'Hadoop':doc_frequency['hadoop'],
                           'MapReduce':doc_frequency['mapreduce'],
                           'Spark':doc_frequency['spark'],
                           'Pig':doc_frequency['pig'],
                           'Hive':doc_frequency['hive'],
                           'Shark':doc_frequency['shark'],
                           'Oozie':doc_frequency['oozie'],
                           'ZooKeeper':doc_frequency['zookeeper'],
                           'Flume':doc_frequency['flume'],
                           'Mahout':doc_frequency['mahout']})
                
    database_dict = Counter({'SQL':doc_frequency['sql'],
                             'NoSQL':doc_frequency['nosql'],
                             'HBase':doc_frequency['hbase'],
                             'Cassandra':doc_frequency['cassandra'],
                             'MongoDB':doc_frequency['mongodb']})
    
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
Useful resources:
    1. Test Python Regex: http://pythex.org/

Refs:
    1. Indeed web scraping project: https://jessesw.com/Data-Science-Skills/
    2. Sample text mining project: http://www.cs.duke.edu/courses/spring14/compsci290/assignments/lab02.html
    3. Data science skills tree: http://nirvacana.com/thoughts/becoming-a-data-scientist/
"""

#------------------------------------------------------------------------------