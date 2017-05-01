# To run the webdriver on Linux
WebDriver download link: https://github.com/mozilla/geckodriver/releases

-----------------------------------------------------------------------------------------
Method 1: Selenium 2.53.6 and Firefox under version 47 (Recommended)
-----------------------------------------------------------------------------------------

1. Modify and run this line in the terminal to add this path to the system
 
   export PATH=$PATH:/path/to/directory/of/executable/downloaded/in/previous/step

   For example:
   export PATH=$PATH:/home/minh/Python/WebScrapping/webdriver

2. If it does not work, downgrade selenium: pip install selenium==2.53.6

3. Downgrade Firefox to version 46

   List all versions:
   apt-cache show firefox | grep Version

   Get previous version:
   sudo apt-get install firefox=28.0+build2-0ubuntu2

   Ref: http://fullstacktutorials.blogspot.fr/2016/06/how-to-downgrade-firefox-version-on.html

-----------------------------------------------------------------------------------------
Method 2: Selenium 3 and Firefox from version 47 (send_keys() mays not work)
-----------------------------------------------------------------------------------------

1. Download newest webdriver, unzip

2. Copy the geckodriver file into /user/local/bin/
