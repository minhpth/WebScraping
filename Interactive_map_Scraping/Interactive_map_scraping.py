#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import print_function, division

"""
Created on Sat May  6 03:12:15 2017

@author: minh
"""

#------------------------------------------------------------------------------
# INTERACTIVE MAP SCRAPING
#------------------------------------------------------------------------------

"""
This project is aiming to extract information from a interactive map.
URL: https://www.gencon.com/map?lt=20.673905264672843&lg=9.931640625000002&z=4&f=1&c=13&hl=1545

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
            
def extract_exhibitorInfo(areaExhibitorList):
    """
    This function loop through all exhibitor areas, click on it and extract their
    information (text and links).
    """
    
    # Loop through all exhibitor areas, click on it and get the information
    exhibitorNameList = []
    exhibitorURLList = []
    
    count_clickableArea = 0
    count_unclickableArea = 0
    count_areaWithURL = 0
    count_areaWithoutURL = 0
    
    error_areaExhibitorList = []
    
    for area in areaExhibitorList:
        
        try:
            
            # Bring object in front
            #driver.execute_script("""$('[d="%s"]').css({position:'absolute'});""" % (area.get_attribute('d')))
            
            # Try to click
            action = ActionChains(driver)
            action.click(area)
            
            # Wait until the popup window showing up
            action.perform()
            contentWrapper = wait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'leaflet-popup-content-wrapper')))
            
            # Extract information
            contentBox = contentWrapper.find_element_by_class_name('leaflet-popup-content')
            exhibitorName = set(contentBox.text.split('\n'))
            
            for t in exhibitorName:
                try:
                    url = contentBox.find_element_by_xpath(".//*[contains(@title, '%s')]" % (t))
                    #print(t, ':', url.get_attribute('href'))
                    
                    exhibitorNameList.append(t)
                    exhibitorURLList.append(url.get_attribute('href'))
                    count_areaWithURL += 1
                except:
                    #print(t, ':', 'NO URL')
                    
                    exhibitorNameList.append(t)
                    exhibitorURLList.append(None)
                    count_areaWithoutURL += 1
                    pass
            
            # Close popup window
            closeButton = driver.find_element_by_class_name('leaflet-popup-close-button')
            closeButton.click()
            
            # Wait until popup disapear
            wait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'leaflet-popup-close-button')))
            
            # If click successfully, change the color of the block to black
            driver.execute_script("""$('[d="%s"]')[0].style.fill = "black";""" % (area.get_attribute('d')))
            count_clickableArea += 1
            
            driver.execute_script("""$('[d="%s"]').hide();""" % (area.get_attribute('d')))
        
        except:
            print('Cannot click this object d =', area.get_attribute('d'))
            update_errorLog('CANNOT_CLICK_OBJECT' + ' | ' + 'd = ' + area.get_attribute('d'))
            driver.execute_script("""$('[d="%s"]')[0].style.fill = "red";""" % (area.get_attribute('d')))
            count_unclickableArea += 1
            error_areaExhibitorList.append(area)
            
        #sleep(0.5)
    
    # Create output table
    exhibitorTb = pd.DataFrame({'exhibitor_name':pd.Series(exhibitorNameList),
                                'exhibitor_url':pd.Series(exhibitorURLList)},
                               columns=['exhibitor_name',
                                        'exhibitor_url'])
    
    return exhibitorTb, error_areaExhibitorList, count_clickableArea, count_unclickableArea, count_areaWithURL, count_areaWithoutURL

def extract_exhibitorInfo2(areaExhibitorList):
    """
    This function loop through all exhibitor areas, click on it and extract their
    information (text and links).
    
    Note: if this while loop runs forever, click on the map by yourself to show
    the text boxes, this function will catch them and finish the rest work.
    
    Currently, there is a clicking issue without solutions.
    """
    
    # Loop through all exhibitor areas, click on it and get the information
    exhibitorNameList = []
    exhibitorURLList = []
    
    while True:
    
        area = areaExhibitorList[0] # Take the first item from queue
        
        try:
            
            # Bring object in front
            #driver.execute_script("""$('[d="%s"]').css({position:'absolute'});""" % (area.get_attribute('d')))
            
            # Try to click
            action = ActionChains(driver)
            action.click(area)
            
            # Wait until the popup window showing up
            action.perform()
            contentWrapper = wait(driver, 5).until(EC.visibility_of_element_located((By.CLASS_NAME, 'leaflet-popup-content-wrapper')))
            
            # Extract information
            contentBox = contentWrapper.find_element_by_class_name('leaflet-popup-content')
            exhibitorName = set(contentBox.text.split('\n'))
            
            for t in exhibitorName:
                try:
                    url = contentBox.find_element_by_xpath(".//*[contains(@title, '%s')]" % (t))
                    #print(t, ':', url.get_attribute('href'))
                    
                    exhibitorNameList.append(t)
                    exhibitorURLList.append(url.get_attribute('href'))
                except:
                    #print(t, ':', 'NO URL')
                    
                    exhibitorNameList.append(t)
                    exhibitorURLList.append(None)
                    pass
            
            # Close popup window
            closeButton = driver.find_element_by_class_name('leaflet-popup-close-button')
            closeButton.click()
            
            # Wait until popup disapear
            wait(driver, 10).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'leaflet-popup-close-button')))
            
            # If click successfully, change the color of the block to black
            driver.execute_script("""$('[d="%s"]')[0].style.fill = "black";""" % (area.get_attribute('d')))
            driver.execute_script("""$('[d="%s"]').hide();""" % (area.get_attribute('d'))) # Hide the clicked block
            
            # Remove the first item of the queue
            del areaExhibitorList[0]
            if len(areaExhibitorList) == 0: break
        
        except:
            print('Cannot click this object d =', area.get_attribute('d'))
            update_errorLog('CANNOT_CLICK_OBJECT' + ' | ' + 'd = ' + area.get_attribute('d'))
            driver.execute_script("""$('[d="%s"]')[0].style.fill = "red";""" % (area.get_attribute('d')))
            
            # Move the failed block to the end of the queue
            del areaExhibitorList[0]
            areaExhibitorList.append(area)
            
        #sleep(0.5)
    
    # Create output table
    exhibitorTb = pd.DataFrame({'exhibitor_name':pd.Series(exhibitorNameList),
                                'exhibitor_url':pd.Series(exhibitorURLList)},
                               columns=['exhibitor_name',
                                        'exhibitor_url'])
    
    return exhibitorTb

#------------------------------------------------------------------------------
# MAIN
#------------------------------------------------------------------------------

if __name__ == '__main__':
    
    #--------------------------------------------------------------------------
    # STEP 1. INITIATING
    #--------------------------------------------------------------------------
    
    # Change os directory
    os.chdir('/home/minh/Python/WebScraping/Interactive_map_Scraping')
    
    # Check log and outut folder exist in current folder
    if not os.path.exists('log'): os.makedirs('log')
    if not os.path.exists('output'): os.makedirs('output')
    
    # Open a web browser with the given url
    url = "https://www.gencon.com/map?lt=17.5602465032949&lg=35.37597656250001&z=4&f=1&c=13"
    driver = web.Firefox()
    driver.set_window_position(0, 0)
    driver.maximize_window()
    driver.get(url)    
    
    # Wait a bit for the page to load
    sleep(5) # 5 secs
    
    # Zoom the screen to see full map
    html = driver.find_element_by_tag_name("html")
    #for i in range(3): html.send_keys(Keys.CONTROL, Keys.SUBTRACT) # Zoom out 3 times
    
    #--------------------------------------------------------------------------
    # STEP 2. FIND ALL CLICKABLE OBJECTS
    #--------------------------------------------------------------------------
    
    # Find all exhibitor areas
    mapObject = driver.find_element_by_css_selector('#interactive-map > div.leaflet-pane.leaflet-map-pane > div.leaflet-pane.leaflet-overlay-pane > svg')
    areaExhibitorList = mapObject.find_elements_by_css_selector(".area-exhibitor.leaflet-interactive") # Get all child objects
    
    # Close the first popup window (if any)
    try:
        closeButton = driver.find_element_by_class_name('leaflet-popup-close-button')
        closeButton.click()
    except:
        pass
    
    #exhibitorTb, error_areaExhibitorList, count_clickableArea, count_unclickableArea, count_areaWithURL, count_areaWithoutURL = extract_exhibitorInfo(areaExhibitorList)
    #exhibitorTb2, error_areaExhibitorList2, _, _, _, _ = extract_exhibitorInfo(error_areaExhibitorList)
    
    exhibitorTb = extract_exhibitorInfo2(areaExhibitorList)
    exhibitorTb.to_csv('output/exhibitorInfo.csv', index=False, encoding='utf-8')
    
    # Check sum
#    print('Verified:', len(areaExhibitorList) == (count_unclickableArea + count_clickableArea))
#    print('Total objects:', len(areaExhibitorList))
#    print('Total clickable objects:', count_clickableArea)
#    print('Total unclickable objects:', count_unclickableArea)
#    print('Total areas with URL:', count_areaWithURL)
#    print('Total areas without URL:', count_areaWithoutURL)
#    print(exhibitorTb.shape)
#    
    #--------------------------------------------------------------------------
    # Debug
    #--------------------------------------------------------------------------
    
    #d = 'M371 101L371 116L343 116L343 251L483 251L483 152L504 152L504 133L463 123L414 123L414 112z'
    #b = mapObject.find_element_by_xpath(""".//*[contains(@d, '%s')]""" % (d))
    
    #driver.execute_script("""$('[d="%s"]').css({position:'absolute'});""" % (d))
    #driver.execute_script("""$('[d="%s"]')[0].style.fill = "black";""" % (d))
    
#------------------------------------------------------------------------------
# Refs
#------------------------------------------------------------------------------

"""
"""

#------------------------------------------------------------------------------