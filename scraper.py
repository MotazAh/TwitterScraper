import time
from utils import user_data
import re
from datetime import datetime, timezone
from multiprocessing import Process, Manager
import random

from selenium import webdriver
from selenium.webdriver import ChromeOptions, ActionChains
from selenium.webdriver.common.by import By

MAX_PROCESSES = 5 # Do specified processes at a time

# Scrapes several account URLs in parallel and repeat after time interval
def scrape_accounts(return_list, symbol:str, accounts, time_interval:int=15, verbose=2):
    # Remove empty url lines
    for account in accounts:
        if account == '':
            account.remove(account)
    while True:
        processes = []
        print('Starting processes...')
        # Do 5 processes at a time
        for i in range(0, len(accounts), 1):
            
            # Skip empty url line
            if accounts[i] == '':
                continue
            
            # Set process and start it
            proc = Process(target=scrape_for_symbol, args=(return_list , symbol, accounts[i], time_interval, verbose))
            processes.append(proc)
            proc.start()
            if verbose >= 1:
                print('Process for ' + accounts[i] + ' started')
            
            # Check if max processes is reached or at last account url
            if len(processes) % MAX_PROCESSES == 0 or (i + 1) == len(accounts):
                for proc in processes:
                    proc.join()
                print("Processes done")

            
        total_matches = len(return_list)
        message = '------ "' + symbol[1:] + '" was mentioned "' + str(total_matches) + '" times in the last "' + str(time_interval) + '" minutes ------'
        print('\n' + message + '\n')
        with open('log.txt', 'a') as f:
            f.write(message + '\n')
        print('Waiting ' + str(time_interval) + ' minutes for next scrape')
        time.sleep(time_interval * 60)

# Searches through chosen user's posts for given symbol in a specific time interval
def scrape_for_symbol(return_list, symbol, url:str, time_interval, verbose):
    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument('log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('prefs', {"profile.managed_default_content_settings.images": 2}) # Avoid loading images

    driver = webdriver.Chrome(options=options)
    if verbose > 0:
        print('Started Chrome Driver')
    
    # First get request to get correct domain for cookies
    if verbose > 0:
        print('Navigating to https://twitter.com')
    driver.get("https://twitter.com")

    # Cookies for login session
    driver.add_cookie({'name': '_twitter_sess', 'value': user_data.get_session(), 'domain': 'twitter.com', 'path': '/'})
    driver.add_cookie({'name': 'auth_token', 'value': user_data.get_auth(), 'domain': 'twitter.com', 'path': '/'})
    driver.add_cookie({'name': 'twid', 'value': user_data.get_twid(), 'domain': 'twitter.com', 'path': '/'})

    # Get user page
    if verbose > 0:
        print('Navigating to ' + url)
    driver.get(url)

    time.sleep(2.5)
    
    if verbose > 0:
        print('Getting cash tag count for ' + url.replace('https://twitter.com/', ''))
    passed_timestamps = []
    while True:
        # Scroll down and sleep for a random amount of time (to avoid getting detect and blocked)
        ActionChains(driver).scroll_by_amount(0, 2000).perform()
        rand_sleep()
        
        # Get posts loaded in driver
        try:
            posts = driver.find_elements(By.XPATH, ".//article[@data-testid='tweet']")
        except:
            return # No posts from user
        exp = re.compile(symbol, re.IGNORECASE)

        new_post_exists = False # Flag to check if last post by the user is reached
        
        # Go through all posts and try to find cash symbol
        if posts:
            for post in posts:
                is_repost = False
                try:
                    tweet_text = post.find_element(By.XPATH, ".//div[@data-testid='tweetText']").text
                    tweet_time = post.find_element(By.XPATH, './/time').text
                except:
                    continue # Skip post containing no text
                tweet_time_stamp = post.find_element(By.XPATH, './/time').get_attribute('datetime')
                ts = time.strptime(tweet_time_stamp,'%Y-%m-%dT%H:%M:%S.000Z') # Format twitter timestamp to datetime stamp
                
                # Skip posts that have been scraped before
                if ts in passed_timestamps:
                    continue
                
                new_post_exists = True
                passed_timestamps.append(ts)
                
                # Get time difference between current timestamp and post timestamp
                unix_ts = time.mktime(ts) 
                cur_ts = time.strptime(str(datetime.now(timezone.utc)), '%Y-%m-%d %H:%M:%S.%f+00:00')
                cur_ts = time.mktime(cur_ts)
                time_difference = cur_ts - unix_ts
                
                # Check if post is a repost or pinned
                try:
                    pinned = post.find_element(By.XPATH, ".//div[@data-testid='socialContext']")
                    if (pinned.text == 'Pinned'):
                        continue
                except:
                    pass
                try:
                    repost = post.find_element(By.XPATH, ".//span[@data-testid='socialContext']")
                    if repost.text.find('reposted'):
                        is_repost = True
                except:
                    pass
                
                # Check if post is outside time interval
                if not is_repost:
                    if time_difference > time_interval * 60:
                        # End scraping session
                        driver.quit()
                        return 
                
                if tweet_text and verbose >= 2:
                    print(url + ' -> ' + str(tweet_time) + ' -- ' + str(tweet_time_stamp) + ' -- ' + str(time_difference), end=' ')
                
                if re.search(exp, tweet_text): # Search for a cash symbol match in text and append to result
                    if verbose >= 2:
                        print("Found match", end=' ')
                    return_list.append(1) # Append the cash symbol count
                if verbose >= 2:
                    print('')
        if not new_post_exists:
            return

# Sleep for a random amount of time
def rand_sleep():
    rand_time = random.randrange(0, 50) / 100
    time.sleep(1 + rand_time)