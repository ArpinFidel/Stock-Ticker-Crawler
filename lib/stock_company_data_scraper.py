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
		
		
def get_company_data(browser):
	url = 'https://www.idx.co.id/data-pasar/data-saham/daftar-saham/'
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