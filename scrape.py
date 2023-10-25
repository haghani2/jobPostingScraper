#!/usr/local/bin/python3
import linkedin as li
import pandas as pd
from os.path import exists

# Note: LinkedIn only shows up to 1000 listings per search result, 
# recommended to use the same search query with different filter
# combinations for the best results.

# WARNING: linkedin.py uses multiprocessing to process multiple URLs, 
# so scraping many URLs at once may be very resource intensive.

# Change to URLs you wish to scrape.
#https://www.linkedin.com/jobs/search?keywords=Data%20Engineer&location=Canada&locationId=&geoId=101174742&f_TPR=r604800&position=1&pageNum=0
urls = ['https://www.linkedin.com/jobs/search?keywords=Sustainability&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://www.linkedin.com/jobs/search?keywords=Data%20Engineer&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://www.linkedin.com/jobs/search?keywords=Data%20Scientist&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://www.linkedin.com/jobs/search?keywords=Computer%20Engineer&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://ca.linkedin.com/jobs/search?keywords=Mechanical%20Engineer&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://ca.linkedin.com/jobs/search?keywords=Robotics%20Engineer&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://ca.linkedin.com/jobs/search?keywords=Data%20Analyst&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
		'https://ca.linkedin.com/jobs/search?keywords=Software%20Project%20Manager&location=Canada&locationId=&geoId=101174742&f_TPR=r86400&position=1&pageNum=0',
]

if __name__ == '__main__':
	# get listings and drop null full_urls
	#df: pd.DataFrame = li.get_listings_from(urls).dropna(axis=0, subset='full_url')
	#drop full_url column from df
	df: pd.DataFrame = li.get_listings_from(urls)
	pd.set_option('display.max_columns', None)

	# drop duplicates
	#df.drop_duplicates(subset='full_url', inplace=True)

	# save to csv file, appending to it if it exists
	if exists('linkedin-job-data.csv'):
		#read csv as old.df
		old_df = pd.read_csv('linkedin-job-data.csv')
		#concatenate old.df and new.df and keep unique records
		df = pd.concat([old_df, df]).drop_duplicates(keep=False)
		df.to_csv('linkedin-job-data.csv', mode='a', index=False, header=False)
	else:
		df.to_csv('linkedin-job-data.csv', mode='w', index=False)	
