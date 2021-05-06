#######################################################################################################################################
# When this script was created there was no official api for power bi so selenium was used to distribute a pdf of dashboard internally#
#######################################################################################################################################
import json, os, time
from selenium import webdriver
from os import path
from PIL import Image

from webdriver_manager.chrome import ChromeDriverManager

### Parms for windows login##
client_id = {}
tenant= {}
driver = webdriver.Chrome(ChromeDriverManager().install())
LOGIN_URL='' # you will have to get redirect link of sso for your company by copying from browser after clicking on dashboard
wndw_email = open('Python_Automation/KyGen/User.txt').read()
wndw_pwd = open('Python_Automation/KyGen/Kys.txt').read()
#############################
## Parms for generating PDF##
#############################
target = "" #add your target path
source = "" # add alt src 
if path.exists(source):
    os.remove(source)
if path.exists(target):
    os.remove(target)
##############################


class WindowsLogin():
    def __init__(self, email, password, browser='Chrome'):
        # Store credentials for login
        self.email = email
        self.password = password
        self.driver = driver
        self.driver.get(LOGIN_URL)
        time.sleep(1)  # Wait for some time to load

    def login(self):
        #send user#
        time.sleep(2)
        email_element = self.driver.find_element_by_xpath('//*[@id="i0116"]')
            #find_element_by_id('i0116')
        email_element.send_keys(self.email)  # Give keyboard input
        # Send mouse click#
        time.sleep(2) # Wait for 2 seconds for the page to show up
        login_button = self.driver.find_element_by_id('idSIButton9')
        login_button.click()
        time.sleep(2) # Wait for 2 seconds for the page to show up
        #send password#
        time.sleep(2) # Wait for 2 seconds for the page to show up
        password_element = self.driver.find_element_by_name('passwd')
        password_element.send_keys(self.password)  # Give password as input too
        # Send mouse click#
        login_button2 = self.driver.find_element_by_id('idSIButton9')
        login_button2.click()
        time.sleep(15)  # Wait for 20 seconds for the page to show up before creating screenshot
        file_button = self.driver.find_element_by_xpath('//*[@id="exploration-container-app-bars"]/app-bar/div/div[1]/button[2]')
            #find_element_by_xpath('//li[1]//button[1]')
        file_button.click()
        time.sleep(3)
        export_button = self.driver.find_element_by_xpath('//*[@id="mat-menu-panel-7"]/div/button[2]')
            #find_element_by_css_selector('.pbi-glyph-pdf')
        export_button.click()
        time.sleep(5)
        # new drop down added by microsoft made ccs element obsolete changed to xpath 2020-09-27 11:32 AM#
        export_drop_down = self.driver.find_element_by_xpath('//dialog-footer/button')
        export_drop_down.click()
        time.sleep(2)
        #new drop down added by microsoft made element below obsolete replaced with code above#
        #export_submit = self.driver.find_element_by_css_selector('.primary')
        #export_submit.click()
        while not os.path.exists(target):
            time.sleep(4)
if __name__ == '__main__':
    # Enter your login credentials here
    wn_login = WindowsLogin(email=wndw_email, password=wndw_pwd, browser='Chrome')
    wn_login.login()
########################################
########### Gen PDF for Email###########
########################################
chrome_options = webdriver.ChromeOptions()
settings = {"recentDestinations": [{"id": "Save as PDF", "origin": "local", "account": ""}], "selectedDestinationId": "Save as PDF", "version": 2}
prefs = {'printing.print_preview_sticky_settings.appState': json.dumps(settings)}
chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--kiosk-printing')
os.remove(source)
driver.quit()

########################################
