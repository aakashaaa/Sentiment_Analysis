import warnings
warnings.filterwarnings("ignore")

import os
import pandas as pd
import re

from selenium.webdriver import *
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver import Chrome
import selenium.webdriver.support.ui as ui
from selenium.webdriver.common.keys import Keys

import chromedriver_binary

import requests
import urllib.request

import time

import sys
# Libraries for Login Credentials Console box
import tkinter as tk

from bs4 import BeautifulSoup
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Adding Chrome Options and driver
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")


# Import file
inputs = pd.read_excel('inputs.xlsx')
inputs.head

# Fetch names and number of posts from the file imported
Names = inputs['Names'].str.strip()
top_n_posts=inputs['N_Posts'][0]
print("The number of posts to look at for each profile : ",top_n_posts)

# Getting chrome path
chrome_path = os.path.dirname(chromedriver_binary.__file__)
chromedriver = (r"%s\chromedriver.exe" %chrome_path)
print("Chrome driver path : ",chromedriver)

chrome_options = Options()

# Private browsing
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--start-maximized")
#chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
driver.get('https://www.news.google.com/')

print(driver.title)  #Prints the title of page


def search(name, num):
	# Defining Searching function which goes to web.google.com and enters the name we want the news for

    inputboxes = driver.find_elements_by_xpath("//input[@aria-label='Search']")

    inputboxes[0].click()
    time.sleep(2)
    inputboxes[0].send_keys(Keys.CONTROL + "a")
    time.sleep(2)
    inputboxes[0].send_keys(Keys.DELETE)
    time.sleep(2)
    inputboxes[0].send_keys(name)
    inputboxes[0].send_keys(Keys.RETURN)
    time.sleep(10)

    driver.refresh()
    
    try:
        for i in range(0,num):
            link1 = []
            text = ' '
            url_string = ' '
            url_obj_share = driver.find_elements_by_xpath("//*[@id='yDmH0d']/c-wiz/div/div[2]/div[2]/div/main/c-wiz/div[1]/div/div/article/a")[i]
            url_string_share = url_obj_share.get_attribute("href")
            print(url_string_share)
            
            link1.append(name)
            
            for k in url_string_share:
                url_string += k
            
            link1.append(url_string)
            
            # Gets text from website using web_text function
            text = web_text(url_string_share)
            print(len(text))
            link1.append(text)
            
            # Gets sentiment of text using sentiment_scores function
            sentiment = sentiment_scores(text)
            link1.append(sentiment)
            
            output.append(link1)
            
    except Exception as e: # Generally gets used when the particular name doesn't come up with any link over google news
        
            link1.append(name)
            link1.append('No links due to error')
            link1.append('NA')
            link1.append(0)
            output.append(link1)
            
            print(e)
            pass


def web_text(link):
    # Helps us to get text from the website

    text1 = ''
    main_window = driver.current_window_handle
    resp=requests.get(link, verify=False)
    output_empty = False

    if resp.status_code==200:
        print("Successfully opened the web page")
        soup=BeautifulSoup(resp.text,'html.parser') 
        text1 = soup.find_all(text=True)
        output = ''
        blacklist = ['[document]','noscript','header','html','meta','head', 'input','script','style','footer']
        #  there may be more elements you don't want, such as "style", etc.
        
        for t in text1:
            if t.parent.name not in blacklist:
                output += '{} '.format(t)

     
    else:      
        print("Didn't successfully opened")

        first_link = driver.find_element_by_tag_name('a')
        first_link.send_keys(Keys.CONTROL + Keys.RETURN)

        # Checking if the post opened is a image or not
        main_url = driver.current_url
        driver.switch_to_window(driver.window_handles[1])
        driver.get(link)
                
        wait_for_page_to_load(driver,20)
        current_url = driver.current_url
        
        if(main_url == current_url):
            driver.close()
            driver.switch_to_window(main_window)
            
        else:
            # if there is some error in new page then continue to next post
            html_page = driver.page_source
            soup=BeautifulSoup(html_page,'html.parser') 
            text1 = soup.find_all(text=True)
            output = ''
            blacklist = ['[document]','noscript','header','html','meta','head', 'input','script','style','footer']
                            # there may be more elements you don't want, such as "style", etc.
            for t in text1:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)
            driver.close()
            driver.switch_to_window(main_window)
    
    # Below if statement will be used when the link opened successfully but didn't allowed us to scrap the text
    if len(output) < 10:    
        print("Output lenght is low, lets try something else")
        first_link = driver.find_element_by_tag_name('a')
        first_link.send_keys(Keys.CONTROL + Keys.RETURN)

        # Checking if the post opened is a image or not
        main_url = driver.current_url
        driver.switch_to_window(driver.window_handles[1])
        driver.get(link)
        
        # all_url_string = all_url_string + url_string
        
        wait_for_page_to_load(driver,20)
        current_url = driver.current_url
        if(main_url == current_url):
            driver.close()
            driver.switch_to_window(main_window)
        else:
            # if there is some error in new page then continue to next post
            html_page = driver.page_source
            soup=BeautifulSoup(html_page,'html.parser') 
            text1 = soup.find_all(text=True)
            output = ''
            blacklist = ['[document]','noscript','header','html','meta','head', 'input','script','style','footer']
                            # there may be more elements you don't want, such as "style", etc.
            for t in text1:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)
            driver.close()
            driver.switch_to_window(main_window)
       
    
    return output

def wait_for_page_to_load(driver,timeout):
	# As name suggest, helps in staying on page till it is loaded completely

    print('wait_for_page_to_load()')
    time_taken = 0
    try:
        
#         print(page_ready)
        while (page_ready != 'complete'):
            page_ready = driver.execute_script("return document.readyState")
            print(page_ready)
            if (time_taken <= timeout):
                time.sleep(1)
                time_taken = time_taken + 1
            else:
                raise        
    except Exception:
        print("Timed out waiting for page to load")
    print('wait_for_page_to_load() ends')

####
# Below are two libraries / functions which gives us sentiment analysis, I personally prefered VaderSentiment because it gave me better results
####

# VaderSentiment Analysis
def sentiment_scores(sentence): 
    
    sid_obj = ' '
    sid_obj = SentimentIntensityAnalyzer() 
    sentiment_dict = sid_obj.polarity_scores(sentence)
    return(sentiment_dict['compound'])

# Text Blob Sentiment Analysis
def sentiment_scores_2(sentence): 
    analysis = TextBlob(sentence)
    return analysis.sentiment.polarity



# Calling the function (Main function)

global output
output = []
for i in Names:
	output.append(search(i, int(top_n_posts)))

# Getting some 'None' values, had to remove those
for i in range(0,len(Names)):
    output.remove(None)

# Finally taking out the output

# We will have 4 columns Name, URL, Web text and Sentiment
final = pd.DataFrame(output, columns=['Name', 'URL','Web_Text','Sentiment'])

final.to_excel("Final.xlsx")

driver.close()   #Closes the browser