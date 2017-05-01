#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Thu Apr 27 19:21:40 2017

@author: minh
"""

#------------------------------------------------------------------------------
# WEB SCRAPING - UPWORK PROJECT - DASHBOARD SCRAPING
#------------------------------------------------------------------------------

"""
This project is aiming to extract information from a dashboard of the website bellow
URL: http://www.estadao.com.br/infograficos/cidades,as-mortes-com-motivacao-politica-no-pais,196294

Note:
    1. Zoom the browser to show full of the dashboard and map.
    2. Move the mouse out of the map before running the script.
    3. Do not click in the dashboard will running the script.
    4. Do not let the screen turn off (or lock) during the script running.

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

# If selenium does not run, downgrade it: pip install selenium==2.53.6
from selenium import webdriver as web # Open a web browser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException, StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

# Other packages
import os
import numpy as np
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

def get_table_data(soup, table_id):
    """
    This function will look for the table by its name (id), then extract data
    and return it in data frame format
    """
    
    # Extract table object
    tbObject = soup.find('ul', attrs={'id':table_id})
    
    nameList = []
    numberList = []
    
    # Loop for all fields in the table to extract data
    for item in tbObject.findAll('li'):
        name = item.find(attrs={'class':'ufBlock'}).text
        number = int(item.find(attrs={'class':'ufAmount'}).text)
        nameList.append(name)
        numberList.append(number)
        
    # Create a data frame ad return the result
    tb = pd.DataFrame({'Item':pd.Series(nameList),
                       'Number':pd.Series(numberList)})
    return tb

def get_circle_data(driver):
    """
    This function will look for all the circles in the map, filter out circles
    with no data (r = 0) and extract data from the rest circle. Return the
    result in data frame format.
    """
    
    def action_wrapper(action, num_retry=3, delay=5):
        """
        This function will try to hover the mouse several times if it gets errors
        """
        
        count_retry = 0
        while count_retry < num_retry:
            try:
                action.perform()
                description = wait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[*[contains(text(), ":")]]'))).text
                return description
                                  
            except:
                print('Error! Circle ID:', circle.get_attribute('id'))
                print('Try again..')
                count_retry += 1
                
                # Move mouse out of the circle
                action2 = ActionChains(driver)
                action2.move_by_offset(10, 10)
                action2.perform()
                sleep(delay) # Then wait
    
    # Extract circle objects
    circleObject = driver.find_element_by_id('circles')
    circleList = circleObject.find_elements_by_css_selector('circle')
    
    circleNameList = []
    circleDataList = []
    
    # Loop through all circles and extract ther radius, sort by descending,
    # and arrange the circleList by that descending order
    rList = [float(circle.get_attribute('r')) for circle in circleList]
    rIndex = np.argsort(-np.array(rList))
    circleList_sorted = [circleList[i] for i in rIndex]
    
    # Loop through all circles and miminize their radius (r = 1)
    for circle in circleList_sorted:
        
        if float(circle.get_attribute('r')) > 0: # Check if circle has data or not (r != 0)
        
            circleId = circle.get_attribute('id')
            driver.execute_script('document.getElementById("%s").setAttribute("r", "0.1");' % (circleId))

    # Loop through all circles and extract their data (if any)
    for circle in circleList_sorted:
        
        if float(circle.get_attribute('r')) > 0: # Check if circle has data or not (r != 0)
        
            action = ActionChains(driver)
            action.move_to_element(circle)
            #action.click(circle)
            
            # Zoom circle before move mouse in
            circleId = circle.get_attribute('id')
            driver.execute_script('document.getElementById("%s").setAttribute("r", "20");' % (circleId))
            driver.execute_script('document.getElementById("%s").style.opacity = "1";' % (circleId))
            
            description = action_wrapper(action)
            
            if description is not None:
                
                #print(description)
                
                # Add new data to the lists
                circleNameList.append(description.split(':')[0].strip())
                circleDataList.append(int(description.split(':')[1].strip().split(' ')[0]))
                
                # Hide circle after extract data
                #driver.execute_script('document.getElementById("%s").style.visibility = "hidden";' % (circleId))
                driver.execute_script('document.getElementById("%s").setAttribute("r", "0.1");' % (circleId))
            
            else:
                print('Error! Circle ID:', circle.get_attribute('id'))
    
    circleTb = pd.DataFrame({'Item':pd.Series(circleNameList),
                             'Number (morte)':pd.Series(circleDataList)})
    return circleTb

def toExcel(name, tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles):
    """
    This function will save all the pandas data frame into 1 Excel file
    """    
    
    # Create a Pandas Excel writer using XlsxWriter as the engine
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    
    # Write each dataframe to a different worksheet
    tb_NORTH.to_excel(writer, sheet_name='tb_NORTH')
    tb_NORDESTE.to_excel(writer, sheet_name='tb_NORDESTE')
    tb_CENTRO_OESTE.to_excel(writer, sheet_name='tb_CENTRO_OESTE')
    tb_SUDESTE.to_excel(writer, sheet_name='tb_SUDESTE')
    tb_SUL.to_excel(writer, sheet_name='tb_SUL')
    tb_circles.to_excel(writer, sheet_name='tb_circles')
    
    # Close the Pandas Excel writer and output the Excel file
    writer.save()
    
def verify(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles):
    """
    This function check sum and duplicate for those input tables
    """    
    
    def check_sum(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles):
        """
        This function will check sum of those above tables to verify the results
        """
        
        s1 = tb_NORTH.iloc[:, 1].sum()
        s2 = tb_NORDESTE.iloc[:, 1].sum()
        s3 = tb_CENTRO_OESTE.iloc[:, 1].sum()
        s4 = tb_SUDESTE.iloc[:, 1].sum()
        s5 = tb_SUL.iloc[:, 1].sum()
        s6 = tb_circles.iloc[:, 1].sum()
        
        if s1 + s2 + s3 + s4 + s5 != s6:
            print(s1 + s2 + s3 + s4 + s5, '!=', s6)
            return False
        else:
            print(s1 + s2 + s3 + s4 + s5, '==', s6)
            return True

    def check_dup(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles):
        """
        This function check duplicate lines in those input tables
        """
        
        l1 = tb_NORTH.shape[0] - tb_NORTH.drop_duplicates().shape[0]
        l2 = tb_NORDESTE.shape[0] - tb_NORDESTE.drop_duplicates().shape[0]
        l3 = tb_CENTRO_OESTE.shape[0] - tb_CENTRO_OESTE.drop_duplicates().shape[0]
        l4 = tb_SUDESTE.shape[0] - tb_SUDESTE.drop_duplicates().shape[0]
        l5 = tb_SUL.shape[0] - tb_SUL.drop_duplicates().shape[0]
        l6 = tb_circles.shape[0] - tb_circles.drop_duplicates().shape[0]
        
        if (l1 == 0) and (l2 == 0) and (l3 == 0) and (l4 == 0) and (l5 == 0) and (l6 == 0):
            print('No duplicated rows')
            return True
        else:
            if l1 != 0: print('Table tb_NORTH has', l1, 'duplicated rows')
            if l2 != 0: print('Table tb_NORDESTE has', l2, 'duplicated rows')
            if l3 != 0: print('Table tb_CENTRO_OESTE has', l3, 'duplicated rows')
            if l4 != 0: print('Table tb_SUDESTE has', l4, 'duplicated rows')
            if l5 != 0: print('Table tb_SUL has', l5, 'duplicated rows')
            if l6 != 0: print('Table tb_circles has', l6, 'duplicated rows')
            return False
    
    if (check_sum(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles) and
        check_dup(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles)):
        return True
    else:
        return False
            
#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    #--------------------------------------------------------------------------
    # STEP 1. INITIATING
    #--------------------------------------------------------------------------
    
    # Change os directory
    os.chdir('/home/minh/Python/WebScraping/Dashboard_scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    # Open a web browser with the given url
    #url = "http://www.estadao.com.br/infograficos/cidades,as-mortes-com-motivacao-politica-no-pais,196294"
    url = "http://infograficos.estadao.com.br/public/cidades/crimes-politicos/"
    driver = web.Firefox()
    driver.set_window_position(0, 0)
    driver.get(url)    
    
    # Wait a bit for the page to load
    #sleep(15) # 15 secs
    wait(driver, 10).until(lambda driver: driver.find_element_by_id('yearPoint0'))
    click_wrapper(driver.find_element_by_id('yearPoint0')) # Click the '1979' button to stop the loading data process
    
    # Zoom the screen to see full map
    html = driver.find_element_by_tag_name("html")
    for i in range(3): html.send_keys(Keys.CONTROL, Keys.SUBTRACT) # Zoom out 3 times
    
    # Create a list of year Id objects
    yearIdList = ['yearPoint' + str(n) for n in range(35)]
         
    # Loop through each year and make a click on the year button
    for year in yearIdList:
        
        # Make the click
        year_button = driver.find_element_by_id(year)
        click_wrapper(year_button) # Click it
        #sleep(5) # Wait a bit for the data to load
        
        # Get year name
        yearText = year_button.get_attribute('href').split('#')[1][1:]
        print('Year:', yearText)
        
        #if int(yearText) < 1997: continue # Debug
        
        # Extract all tables' data
        soup = BeautifulSoup(driver.page_source, "html.parser")
        tb_NORTH = get_table_data(soup, 'graphN')
        tb_NORDESTE = get_table_data(soup, 'graphNE')
        tb_CENTRO_OESTE = get_table_data(soup, 'graphCO')
        tb_SUDESTE = get_table_data(soup, 'graphSE')
        tb_SUL = get_table_data(soup, 'graphS')
        
        # Extract all circles' data
        tb_circles = get_circle_data(driver)
        
        # Save data to Excel file
        name = 'output/' + yearText + 'data.xls'
        toExcel(name, tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles)
        
        # Verify and print out results (wrong from 1997)
        print('Verified:', verify(tb_NORTH, tb_NORDESTE, tb_CENTRO_OESTE, tb_SUDESTE, tb_SUL, tb_circles))
        print()
    
    # Minimize the windows after finishing
    #driver.set_window_position(0, 0)
    
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
http://stackoverflow.com/questions/7781792/selenium-waitforelement
http://stackoverflow.com/questions/17911980/selenium-with-python-how-to-modify-an-element-css-style
http://stackoverflow.com/questions/8473024/selenium-can-i-set-any-of-the-attribute-value-of-a-webelement-in-selenium
http://stackoverflow.com/questions/26143308/check-if-web-object-is-front-of-other-web-object-in-selenium
https://pypi.python.org/pypi/selenium
"""

#------------------------------------------------------------------------------