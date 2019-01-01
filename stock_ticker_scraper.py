from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from lib.stock_company_data_scraper import *
from lib import silence
from time import sleep

import contextlib
import datetime
import os
import pandas

class init_browser(object):
	def __enter__(self):
		runPath = os.path.dirname(os.path.abspath(__file__))
		self.downloadPath = runPath+'\\lib\\downloads'
		self.browserPath = runPath+'\\lib\\chromedriver.exe'
		
		op = webdriver.ChromeOptions()
		prefs = {	'profile.default_content_setting_values': {
						'cookies': 2,
						'images': 2,
						'plugins': 2,
						'popups': 2,
						'geolocation': 2, 
						'notifications': 2,
						'auto_select_certificate': 2,
						'fullscreen': 2, 
						'mouselock': 2,
						'mixed_script': 2,
						'media_stream': 2, 
						'media_stream_mic': 2,
						'media_stream_camera': 2,
						'protocol_handlers': 2, 
						'ppapi_broker': 2,
						'automatic_downloads': 2,
						'midi_sysex': 2, 
						'push_messaging': 2,
						'ssl_cert_decisions': 2,
						'metro_switch_to_desktop': 2, 
						'protected_media_identifier': 2,
						'app_banner': 2,
						'site_engagement': 2, 
						'durable_storage': 2},
					'disk-cache-size': 4096,
					'download.default_directory': self.downloadPath
				}

		args = [
				'headless',
				'--silent',
				'--disable-gpu',
				'--disable-notifications',
				'--log-level=1',
				'--disable-extensions',
				'test-type'
				]

		sargs = ['hide_console']
		
		for arg in args:
			op.add_argument(arg)
		op.add_experimental_option("prefs", prefs)
		
		self.browser = webdriver.Chrome(self.browserPath, options=op, service_args=sargs)

		self.browser.implicitly_wait(20)
		
		return self.browser, self.downloadPath
	
	def __exit__(self, type, value, traceback):
		self.browser.quit()

def get_new_company_data(browser):
	with silence.no_stdout():
		companies = get_company_data(browser)
	
	with open('.\\lib\\companies.txt', 'w+') as companyFile:
		companyFile.write('%s\n' % (datetime.date.isoformat(datetime.date.today())))
		for c in companies:
			companyFile.write('%s^%s^%s^%s^%s\n' % (c.code, c.name, c.recDate, c.stock, c.board))
	
	return companies, datetime.date.today()
	
def read_company_data():
	with open('.\\lib\\companies.txt', 'r') as companyFile:
		companiesLastUpdate = datetime.date.fromisoformat(companyFile.readline().strip())
		companies = [Company(c.split('^')) for c in companyFile.read().splitlines()]
	return companies, companiesLastUpdate

def get_company_data():
	try:
		companies, companiesLastUpdate = read_company_data()
	except FileNotFoundError as fe:
		print('Data not found locally. Downloading data')
		with silence.no_stdout(), init_browser()[0] as browser:
			companies, companiesLastUpdate = get_new_company_data(browser)
	return companies, companiesLastUpdate

def get_new_ticker_data(browser, targetDate):
	
		url = 'https://idx.co.id/data-pasar/ringkasan-perdagangan/ringkasan-saham/'
		browser.get(url)
		
		for i in range(5):
			try:
				Select(browser.find_element(By.NAME, 'stockTable_length')).select_by_value('100')
			except:
				sleep(0.2)
				continue
			break
		else: raise TimeoutError('Unable to change table length')
		
		for i in range(5):
			try:
				calendarText = browser.find_element(By.ID, 'dateFilter')
				calendarText.click()
			except:
				sleep(0.2)
				continue
			break
		else: raise TimeoutError('Unable to locate calendar text element')
		
		for i in range(5):
			try:
				calendarYear = browser.find_element(By.XPATH, '/html/body/div/div[1]/div/div/input')
				calendarYear.click()
				calendarYear.send_keys(str(targetDate.year))
			except:
				sleep(0.2)
				continue
			break
		else: raise TimeoutError('Unable to locate calendar year elements')
		
		while True:
			for i in range(5):
				try:
					for i in range(5):
						try:
							calendarMonthText = browser.find_element(By.XPATH, '/html/body/div/div[1]/div/span')
							calendarMonthPrev = browser.find_element(By.XPATH, '/html/body/div/div[1]/span[1]')
							calendarMonthNext = browser.find_element(By.XPATH, '/html/body/div/div[1]/span[2]')	
						except:
							sleep(0.2)
							continue
						break
					else: raise TimeoutError('Unable to locate calendar month elements')
					
					curMonth = datetime.datetime.strptime(calendarMonthText.get_attribute('innerHTML').strip(), '%B').month
				except:
					sleep(0.05)
					continue
				break
			else: raise TimeoutError('Unable to get calendar month attribute')
			
			if curMonth == targetDate.month: break
			
			for i in range(5):
				try:
					if curMonth > targetDate.month: calendarMonthPrev.click()
					elif curMonth < targetDate.month: calendarMonthNext.click()
				except:
					sleep(0.05)
					continue
				break
			else: raise TimeoutError('Unable to change month')
		
		sleep(1)
		
		for i in range(10):
			try:
				dayString = '%s %d, %d' % (targetDate.strftime('%B'), targetDate.day, targetDate.year)
				day = browser.find_element(By.XPATH, '/html/body/div/div[2]/div/div[2]/div/span[@aria-label="'+ dayString +'"]')
				day.click()
			except:
				sleep(0.2)
				continue
			break
		else: raise TimeoutError('Unable to change day')
		
		sleep(0.5)
		
		for i in range(10):
			try:
				browser.find_element(By.XPATH, '/html/body/main/div[1]/div[5]/button').click()
			except:
				sleep(0.2)
				continue
			break
		else: raise TimeoutError('Unable to find data')
		
		sleep(3)
		
		for i in range(10):
			try:
				browser.find_element(By.XPATH, '/html/body/main/div[2]/div/div[3]/a').click()
			except:
				sleep(0.5)
				continue
			break
		else: raise TimeoutError('Unable to find download button')
		
		time.sleep(5)

def get_ticker_data(browser, downloadPath, targetDate, tickers):
	filePath = 'lib\\downloads\\Ringkasan Saham-' + targetDate.strftime('%Y%m%d.xlsx')
	try:
		# file = pandas.read_excel(filePath, skiprows=1, usecols='B,F:I,L:N')
		file = pandas.read_excel(filePath, skiprows=1, usecols='B,F:J', index_col=0, header=0)
	except FileNotFoundError as fe:
		get_new_ticker_data(browser, targetDate)
		# file = pandas.read_excel(filePath, skiprows=1, usecols='B,F:I,L:N')
		file = pandas.read_excel(filePath, skiprows=1, usecols='B,F:J', index_col=0, header=0)
	for row in file.iterrows():
		if row[0] not in tickers:
			tickers[row[0]] = {}
		
		tickers[row[0]][targetDate] = (row[1]['Open Price'], row[1]['First Trade'], row[1]['Tertinggi'], row[1]['Terendah'], row[1]['Penutupan'])
		
if __name__ == '__main__':
	
	print('Loading company list...')
	
	companies, companiesLastUpdate = get_company_data()
	
	# tickers = pandas.DataFrame({'Open Price':[],'First Trade':[],'Tertinggi':[],'Terendah':[],'Penutupan':[],})
	tickers = {}
	
	with init_browser() as (browser, downloadPath), pandas.option_context('display.max_rows', None, 'display.max_columns', None):
		get_ticker_data(browser, downloadPath, datetime.date(2017,1,20), tickers)
		print(tickers['AALI'][datetime.date(2017,1,20)])
	
	menu = {
		1:'Update company list',
		2:'Show company list',
		3:'Show company ticker',
		4:'Quit'}
	
	while True:
		print('\n%d companies in list' % (len(companies)))
		print('Last updated on: %s' % (companiesLastUpdate.strftime('%A, %d-%b-%Y')))
		for m in menu:
			print('%d. %s' % (m, menu[m]))
		
		cMenu = int(input(' >> '))
		
		if cMenu == 1:
			print('Fetching company list. Please wait.')
			get_new_company_data()
		elif cMenu == 2:
			for c in companies:
				print('Symbol: %s\tName: %s' % (c.code, c.name))
		elif cMenu == 3:
			cSymbol = input(' >> input company symbol: ')
		elif cMenu == 4:
			break
		else:
			print('invalid input')