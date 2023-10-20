from selenium import webdriver

website = 'https://www.browserstack.com/guide/python-selenium-to-run-web-automation-test'
driver = webdriver.Chrome()
driver.get(website)

driver.quit()