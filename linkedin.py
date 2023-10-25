#!/usr/local/bin/python3
import time
import traceback
import re
import sys
import platform
import multiprocessing as mp
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
from tqdm import tqdm
import numpy as np

# Chrome Driver Options
__chrome_options = webdriver.ChromeOptions()
__chrome_options.add_argument("--disable-extensions")
__chrome_options.add_argument("--headless")
__chrome_options.add_argument("--disable-gpu")
__chrome_options.add_argument("window-size=2100,700")
# Chrome Driver Service
webdriver_path = './chromedriver' if platform.system() != 'Windows' else 'chromedriver.exe'
__chrome_service = Service(webdriver_path)

# Returns a data frame containing a job's info from a WebElement
def __scrape_job(job, wd):
    # Job posting title
    title = job.find_element(By.CLASS_NAME, 'base-search-card__title').text

    # clicks the element, sometimes clicking fails so it tries 3 times, scrolling down the page on failure
    for _ in range(3):
        try:
            job.find_element(By.CSS_SELECTOR, 'a').click()
            break
        except:
            wd.execute_script("window.scrollBy(0,500);")
            continue

    """
	Tries to get the full url, company name, company URL, and location of the listing,
	otherwise the information is an np.nan object.
	"""
    try:
        # Full URL of the listing
        full_url = job.find_element(By.CSS_SELECTOR, 'a').get_attribute('href')
        # the url without all trackers and ref stuff
        full_url = re.search(
            r'https:\/\/.*linkedin.com\/jobs\/view\/.+\?', full_url).group(0)
    except:
        full_url = np.nan
    try:
        company = job.find_element(
            By.CLASS_NAME, 'base-search-card__subtitle').text
    except:
        company = np.nan
    try:
        list_date = job.find_element(
            By.CLASS_NAME, 'job-search-card__listdate').get_attribute("datetime")
    except:
        try:
            list_date = job.find_element(
                By.CLASS_NAME, 'job-search-card__listdate--new').get_attribute("datetime")
        except:
            list_date = np.nan
    try:
        company_url = job.find_element(
            By.CSS_SELECTOR, 'h4>a').get_attribute('href')
    except:
        company_url = np.nan
    try:
        location = job.find_element(
            By.CLASS_NAME, 'job-search-card__location').text
    except:
        location = np.nan

    time.sleep(3)

    """
	Attempts to get the description, seniority level, employment type, job function, and industries
	of the listing, missing information is 'Not Assigned' to match other listings
	"""
    try:
        description = wd.find_element(
            By.CLASS_NAME, 'show-more-less-html__markup').get_attribute('innerHTML')
        description = str(description)
    except:
        description = np.nan
    try:
        seniority_level = wd.find_element(
            By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[1]/span').text
    except:
        seniority_level = 'Not Assigned'
    try:
        employment_type = wd.find_element(
            By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[2]/span').text
    except:
        employment_type = 'Not Assigned'
    try:
        job_function = wd.find_element(
            By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[3]/span').text
        job_function = job_function.replace(', and ', ', ')
    except:
        job_function = 'Not Assigned'
    try:
        industries = wd.find_element(
            By.XPATH, '/html/body/div[1]/div/section/div[2]/div/section[1]/div/ul/li[4]/span').text
        industries = industries.replace(', and ', ', ')
    except:
        industries = 'Not Assigned'

    # Creates and returns a data frame containing the job's information.
    job_data = pd.DataFrame({
        'title': [title],
        'full_url': [full_url],
        'company': [company],
        'list_date': [list_date],
        'company_url': [company_url],
        'location': [location],
        'description': [description],
        'seniority_level': [seniority_level],
        'employment_type': [employment_type],
        'job_function': [job_function],
        'industries': [industries],
    })

    return job_data


# Main scraping function
def __scrape(url, bar_position=0):
    # starts the webdriver process
    wd = webdriver.Chrome(service=__chrome_service, options=__chrome_options)
    wd.get(url)
    time.sleep(2.5)

    # The number of listings in the URL
    num_of_jobs = wd.find_element(
        By.XPATH, '/html/body/div[1]/div/main/div/h1/span[1]').text
    num_of_jobs = int(num_of_jobs) if '+' not in num_of_jobs else 1000

    # Variables for the loop
    jobs_data = []  # Array of each individual job's information
    last_scraped_job = 0  # index of the last scraped job
    height = wd.execute_script(
        "return document.documentElement.scrollHeight")  # height of the webpage
    same_position = 0  # counter for how many times the page height has not changed
    # Loop progress bar
    pbar = tqdm(desc='Scraping...', total=num_of_jobs, position=bar_position)
    while True:

        """
        Passes the next job's WebElement to the __scrape_job function, appending the resulting data frame
        to jobs_data. On failure, checks to see if the bottom of the web page has been reached and breaks the loop.
        Otherwise clicks the button to show more listings, if failure and the height of the document does not
        change, loop ends returning listings thus far.
        """
        try:
            xpath = '//*[@id="main-content"]/section[2]/ul/li[{}]'.format(
                last_scraped_job+1)
            next_job = wd.find_element(By.XPATH, xpath)
            jobs_data.append(__scrape_job(next_job, wd))
            last_scraped_job += 1
            pbar.update(1)
        except:
            try:
                bottom = wd.find_element(
                    By.XPATH, '//*[@id="main-content"]/section[2]/div[2]/p')
            except:
                bottom = wd.find_element(
                    By.XPATH, '//*[@id="main-content"]/section[2]/div/p')
            if bottom.is_displayed():
                pbar.close()
                break
            else:
                if same_position >= 5:
                    pbar.close()
                    print('linkedin error not allowing the showing of more jobs')
                    break

                try:
                    wd.find_element(By.CLASS_NAME, 'two-pane-serp-page__results-list').find_element(
                        By.CSS_SELECTOR, 'button').click()
                    time.sleep(2.5)
                    if height == wd.execute_script("return document.documentElement.scrollHeight"):
                        same_position += 1
                        continue
                    else:
                        same_position = 0
                        height = wd.execute_script(
                            "return document.documentElement.scrollHeight")
                        continue
                except:
                    # Unknown error
                    pbar.close()
                    wd.quit()
                    print('\n Unknown Error \n')
                    traceback.print_exc()
                    sys.exit(1)

    # quits the WebDriver, combines the jobs_data array into a single data frame and returns it
    wd.quit()
    print(pd.concat(jobs_data))
    return pd.concat(jobs_data)


# Helper function that calls the scrape function, adding it to the process queue
def __get_jobs(q, url, position):
    q.put(__scrape(url, position))


# Get job listings from a list of LinkedIn search URLs
def get_listings_from(urls: list) -> pd.DataFrame:
    processes = []
    # Create a process queue
    q = mp.Queue()
    # List holding the resulting data frame from each process
    jobs = []
    # CI progress bar position/offset
    position = 0
    for url in urls:
        # Create a process and call '__get_jobs' to add to queue
        p = mp.Process(target=__get_jobs, args=(q, url, position))
        position += 1
        # Start process
        p.start()
        processes.append(p)

    # Collect results from the queue into jobs array
    for p in processes:
        jobs.append(q.get())

    # Ends the processes
    for p in processes:
        p.join()

    # Return a data frame containing all the job listings from the URLs
    print('\nDone Scraping!\n')
    return pd.concat(jobs)
