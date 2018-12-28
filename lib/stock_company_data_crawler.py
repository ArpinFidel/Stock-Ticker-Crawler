from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import os
import time

class Company:
	def __init__(self, data):
		self.code = data[0]
		self.name = data[1]
		self.recDate = data[2]
		self.stock = data[3]
		self.board = data[4]
		
		
def get_company_data(browserPath):

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
				'disk-cache-size': 4096}

	op.add_experimental_option("prefs", prefs)

	op.add_argument('headless')
	op.add_argument("--silent")
	op.add_argument("--disable-gpu")
	op.add_argument('--disable-notifications')
	op.add_argument('--log-level=1')
	op.add_argument("--disable-extensions");
	op.add_argument("test-type")
	
	args = ['hide_console']
	
	
	url = 'https://www.idx.co.id/data-pasar/data-saham/daftar-saham/'

	browser = webdriver.Chrome(browserPath, options=op, service_args=args)

	browser.implicitly_wait(20)

	browser.get(url)

	buttonNext = browser.find_element(By.ID, 'stockTable_next')

	Select(browser.find_element(By.NAME, 'stockTable_length')).select_by_value('100')

	companies = list()

	time.sleep(5)
	
	tableTriesLimit = 50
	rowTriesLimit = 10
	nextTriesLimit = 30
	

	for i in range(7):
		
		print('Currently on page %d' % i)
		print('Retrieved %d data' % len(companies))
		
		tableTries = 0
		while True:
			while  True:
				tableTries = tableTries + 1
				if tableTries > tableTriesLimit: raise RuntimeError('get table timeout')
				try:
					table = browser.find_element(By.ID, 'stockTable').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
					rowNum = int(table[0].find_elements(By.TAG_NAME, 'td')[0].get_attribute('innerHTML'))
				except Exception as e:
					print(e)
					print('Failed getting table. Retrying...')
					continue
				break
				
			if rowNum == i*100+1:
				break
			else:
				time.sleep(0.5)
		
		for row in table:
			rowTries = 0
			while True:
				rowTries = rowTries + 1
				if rowTries > rowTriesLimit: raise RuntimeError('get row timeout')
				try:
					data = [r.get_attribute('innerHTML') for r in row.find_elements(By.TAG_NAME, 'td')[1:]]
				except Exception as e:
					print(e)
					print('Failed getting row. Retrying...')
					continue
				break
			companies.append(Company(data))
		
		nextTries = 0
		while True:
			if nextTries > nextTriesLimit: raise RuntimeError('get next button timeout')
			try:
				buttonNext.click()
			except Exception as e:
				print(e)
				print('Failled moving to next page. Retrying...')
				buttonNext = browser.find_element(By.ID, 'stockTable_next')
				time.sleep(0.5)
				continue
			break
	
	browser.quit()
	return companies
			
if __name__ == '__main__':
	try:
		print('Loading data from https://www.idx.co.id/data-pasar/data-saham/daftar-saham/')
		
		runPath = os.path.dirname(os.path.abspath(__file__))
		browserPath = runPath+'\\lib\\chromedriver.exe'
		
		companies = get_company_data(browserPath)

		outputFile = open('companies.txt','w+')
		for c in companies:
			print('%s^%s^%s^%s^%s' % (c.code, c.name, c.recDate, c.stock, c.board))
			outputFile.write('%s^%s^%s^%s^%s\n' % (c.code, c.name, c.recDate, c.stock, c.board))
		outputFile.close()

		print('Successfully retrieved %d data' % len(companies))

		input('Press enter to quit')
	except Exception as e:
		input(e)